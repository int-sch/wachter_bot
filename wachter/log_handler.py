import html
from logging import WARNING, ERROR, Formatter, LogRecord, StreamHandler
from typing import Callable

from constants import LOG_FORMAT


class ErrorBroadcastHandler(StreamHandler):
    def __init__(self, send: Callable = None):
        if send is None:
            raise ValueError(
                "On initialization must pass send to ErrorBroadcastHandler"
            )
        super().__init__()
        self.setFormatter(Formatter(LOG_FORMAT))
        self.send = send
        self.is_muted = False

    def emit(self, record: LogRecord):
        self.format(record)
        super().emit(record)
        if record.levelno >= WARNING and not self.is_muted:
            error_message = f"{record.levelname} - {record.module} - {record.message}"
            if record.exc_text:
                error_message += f" - {record.exc_text}"
            try:
                self.send(
                    f"<code>{html.escape(error_message)}</code>"
                )
            except Exception as e:
                # if it can't send a message, still should log it to the stream
                super().emit(
                    LogRecord(
                        name=__name__,
                        level=ERROR,
                        pathname=None,
                        lineno=-1,
                        msg=f"Could not send error to telegram: {e}",
                        args=None,
                        exc_info=None,
                    )
                )

    def set_muted(self, is_muted: bool):
        self.is_muted = is_muted
