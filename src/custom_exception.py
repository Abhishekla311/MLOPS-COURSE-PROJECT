import traceback
import sys


class CustomException(Exception):

    def __init__(self, error_message, error_details):

        super().__init__(error_message)

        self.error_message = self.get_detailed_error_message(
            error_message,
            error_details
        )


    @staticmethod
    def get_detailed_error_message(error_message, error_details):

        _, _, exc_tb = sys.exc_info()

        if exc_tb is not None:

            file_name = exc_tb.tb_frame.f_code.co_filename

            line_number = exc_tb.tb_lineno

            return (
                f"Error occurred in file: {file_name}, "
                f"line number: {line_number}, "
                f"error message: {error_message}"
            )

        else:

            return error_message


    def __str__(self):

        return self.error_message