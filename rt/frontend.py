import datetime
import logging
import time
from queue import Queue
from threading import Event, Lock, Thread

from .exc import RTAuthenticationError
from .interface import RTInterface


log = logging.getLogger(__name__)


MAX_WORKER_LIFETIME = datetime.datetime.max.timestamp()
PENDING = object()


class RTFrontEnd:

    """Wraps an :class:`rt.RTInterface` instance.

    It adds thread-safety and robustness to RT API operations.

    When an RT operation fails due to a lack of authorization (or what
    appears to be a lack of authorization), it will automatically be
    retried after logging out and back in again.

    Generally, there should be just one of these per app, instantiated
    during app startup.

    Args:
        num_workers (int): Number of :class:`Worker`s to start. Each will
            have its own RT connection.
        worker_lifetime (int): Number of seconds a :class:`Worker`
            should live before being killed off and replaced.
        wrapped_type (RTInterface): The RT interface type to wrap.
            An instance of this type will be constructed with
            ``**wrapped_args``. A different type can be passed as long
            as it implements the same interface as class:`RTInterface`.
        wrapped_args (**dict): All other keyword args will be used to
            construct instances of ``wrapped_type``.

    """

    def __init__(self, num_workers=2, worker_lifetime=1800, wrapped_type=RTInterface,
                 **wrapped_args):
        self.wrapped_type = wrapped_type
        self.wrapped_args = wrapped_args
        self.task_queue = Queue()
        self.worker_lifetime = worker_lifetime
        self.worker_lock = Lock()
        self.workers = [self.make_worker() for _ in range(num_workers)]

    def make_worker(self):
        wrapped = self.wrapped_type(**self.wrapped_args)
        worker = Worker(wrapped, self.task_queue, self.worker_lifetime)
        worker.start()
        return worker

    def check_workers(self):
        # Replace dead workers
        with self.worker_lock:
            new_workers = []
            for worker in self.workers:
                worker = self.make_worker() if worker.is_dead else worker
                new_workers.append(worker)
            self.workers = new_workers

    def add_task(self, operation, args=(), kwargs=None):
        self.check_workers()
        task = Task(operation, args, kwargs or {})
        self.task_queue.put(task)
        return task

    def get_result(self, task):
        result = task.get_result()  # Waits until result is ready
        if isinstance(result, Exception):
            raise result
        return result

    def add_task_and_wait_for_result(self, operation, args=(), kwargs=None):
        task = self.add_task(operation, args, kwargs)
        return self.get_result(task)

    # Wrapped operations

    def get_ticket(self, ticket_id) -> dict:
        """Return a dict of ticket data fetched from RT."""
        return self.add_task_and_wait_for_result('get_ticket', (ticket_id,))

    def create_ticket(self, data) -> int:
        """Create a ticket in RT.

        On success, this will return the new ticket's ID, which can be
        passed to :meth:`.get_ticket` to get the ticket's data.

        """
        return self.add_task_and_wait_for_result('create_ticket', (data,))

    def update_ticket(self, ticket_id, data) -> int:
        """Update ticket in RT.

        On success, this will return ``ticket_id``.

        """
        return self.add_task_and_wait_for_result('update_ticket', (ticket_id, data))

    def search(self, query, format='i'):
        return self.add_task_and_wait_for_result('search', (query,), {'format': format})


class Worker(Thread):

    def __init__(self, wrapped, task_queue, lifetime=MAX_WORKER_LIFETIME):
        super().__init__(daemon=True)

        self.wrapped = wrapped
        self.task_queue = task_queue

        # A worker expires when the time elapsed from its start time is
        # greater than its lifetime. By default, workers live forever
        # (well, until Dec 31st, 9999 anyway).
        self.lifetime = lifetime
        # These get set when the worker is started.
        self.start_time = None
        self.expires_at = None

        # This flag is set to explicitly kill the worker. Workers are
        # killed when they fail to finish a task.
        self.killed = False

    @property
    def is_dead(self):
        return self.killed or self.has_expired

    @property
    def has_expired(self):
        return time.monotonic() >= self.expires_at

    def start(self):
        self.start_time = time.monotonic()
        self.expires_at = self.start_time + self.lifetime
        return super().start()

    def run(self):
        while not self.is_dead:
            task = self.wait_for_task()
            log.debug('Worker %s got task: %s', self, task)
            try:
                try:
                    result = self.perform_task(task)
                except RTAuthenticationError:
                    # Retry task one time if authentication fails, which
                    # is an indication that the RT session has expired.
                    log.debug('Retrying task...')
                    self.wrapped.logout()
                    result = self.perform_task(task)
            except Exception as exc:
                result = exc
                self.kill()
                log.debug('Worker %s killed', self)
            self.finish_task(task, result)
        self.dispose()

    def kill(self):
        self.killed = True

    def dispose(self):
        try:
            self.wrapped.logout()
        except Exception as exc:
            log.warn('Logout failed while disposing of worker: %s', exc)

    def wait_for_task(self):
        return self.task_queue.get()

    def perform_task(self, task):
        wrapped = self.wrapped
        wrapped.login()
        operation = getattr(wrapped, task.operation)
        result = operation(*task.args, **task.kwargs)
        return result

    def finish_task(self, task, result):
        task.set_result(result)
        self.task_queue.task_done()


class Task:

    __slots__ = ('operation', 'args', 'kwargs', 'ready', 'result')

    def __init__(self, operation, args, kwargs):
        self.operation = operation
        self.args = args
        self.kwargs = kwargs
        self.ready = Event()
        self.result = PENDING

    def get_result(self):
        self.ready.wait()
        return self.result

    def set_result(self, result):
        if self.result is not PENDING:
            raise ValueError('Result already set for this task')
        self.result = result
        self.ready.set()

    def __str__(self):
        return '{0.operation}(*{0.args}, **{0.kwargs})'.format(self)
