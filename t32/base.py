import sys

class T32Interface:
    """Abstract base class for T32 interface"""

    def run(self, args):
        """Run a T32 command"""
        raise NotImplementedError()

    def echo(self, args):
        """Evaluate a t32 expression and return result

        This function converts the result to the appropriate python type
        """
        raise NotImplementedError()

    def error_reset(self):
        return self.run(['ERROR.RESet'])

    def error_occurred(self):
        return self.echo('ERROR.OCCURRED()')

    def error_id(self):
        return self.echo('ERROR.ID()')

    def raise_error_id(self):
        """Raise an exception with ERROR.ID()"""
        error_id = self.error_id()
        if error_id:
            raise Exception("T32 Error {!r}".format(error_id))
