from functools import update_wrapper
import click



@click.group(chain=True)
def cli():
    """CLI
    """


# ---------------------------------------------------------------------------
# Allow multiple chainning cmd see : https://click.palletsprojects.com/en/7.x/commands/#multi-command-pipelines
# and https://github.com/pallets/click/tree/master/examples/imagepipe
# credits: https://github.com/pallets


@cli.resultcallback()
def process_commands(processors):
    """This result callback is invoked with an iterable of all the chained
    subcommands.  As in this example each subcommand returns a function
    we can chain them together to feed one into the other, similar to how
    a pipe on unix works.
    """
    # Start with an empty iterable.
    stream = ()

    # Pipe it through all stream processors.
    for processor in processors:
        stream = processor(stream)

    # Evaluate the stream and throw away the items.
    for _ in stream:
        pass


def processor(f):
    """Helper decorator to rewrite a function so that it returns another
    function from it.
    """

    def new_func(*args, **kwargs):
        def processor(stream):
            try:
                result = f(stream, *args, **kwargs)
                return result
            except Exception as e:
                click.echo(f"Error: {e}", err=True)

        return processor

    return update_wrapper(new_func, f)


def generator(f):
    """Similar to the :func:`processor` but passes through old values
    unchanged and does not pass through the values as parameter.
    """

    @processor
    def new_func(stream, *args, **kwargs):
        yield from stream
        yield from f(*args, **kwargs)

    return update_wrapper(new_func, f)
