"""

"""

from yapsy import IPlugin
import inspect
import re


class ArgTypeError(ValueError):
    """"""
    def __init__(self, *args, layers):
        self.args = args
        self.layers = layers

class ResultFunctionError(ValueError):
    """Errors """
    pass


class ResultFunction(IPlugin):

    PRIO_CORE = 0
    PRIO_COMMON = 10
    PRIO_USER = 20

    NAME_RE = re.compile(r'^[a-z_]+$')

    def __init__(self, name, args_list, args_help, return_type, description,
                 priority=PRIO_COMMON):

        super().__init__()

        if self.NAME_RE.match(name) is None:
            raise ValueError(
                "Invalid ResultFunction plugin name {} in plugin {}"
                .format(name, self.path)
                             )
        self.name = name

        self._validate_arglist(args_list)

        self.arg_types = args_list


        if len(args_help) != len(args_list):
            raise ValueError(
                "You must give an args_help string for each item in the "
                "args_list. Got {args_len} args and {args_help_len} help "
                "items."
                .format(
                    args_len=len(args_list),
                    args_help_len=len(args_help),
                )
            )

        for i in range(len(args_help)):
            arg_help = args_help[i]
            if not arg_help:
                # We're assuming we got a stringish object.
                raise ValueError(
                    "Empty arg_help value for arg {} of {}"
                    .format(i, len(args_help)))

        self.args_help = args_help

        self.return_type = return_type
        self._priority = priority

    def _validate_arglist(self, arglist):

        for i in range(len(arglist)):
            try:
                self._validate_arg(arg)
            except ArgTypeError as err:
                msg = err.args[0]
                location = '.'.join(err.layers)
                raise ResultFunctionError(
                    "ResultFunction plugin {s.name} encountered errors when "
                    "validating its argument list definition. The error "
                    "occurred for argument {arg_n} of {arg_len} at {loc}: \n"
                    "{msg}".format(
                        s=self,
                        arg_n=i,
                        arg_len=len(arglist),
                        loc=location,
                        msg=msg
                    )
                )

    def _validate_arg(self, arg, layers=None):
        if layers is None:
            layers = []

        # Woah, woah, woah, wait a second.
        # Why are you doing type validation in python?
        #   Because in this case we're using these types to define a structure,
        #   and while the types themselves don't really matter, the structure
        #   does and is limited to JSON component types anyway.
        #   Also, to do math on the incoming data we need to know what types
        #   things should be, so we can convert the incoming data to that
        #   type.

        if isinstance(arg, list):
            layers.append('list')

            if len(arg) == 0:
                raise ArgTypeError(
                    "When giving an argument type of a list, it must contain "
                    "the type of the underlying values, but the list was "
                    "empty.",
                    layers=layers

                )
            elif len(arg) > 1:
                raise ArgTypeError(
                    "Got more than one underlying type for a list argument.",
                    layers=layers
                )

            self._validate_arg(arg[0], layers)

        elif isinstance(arg, dict):
            # Each key of the dict must have an associated type,
            # or it should have a single key of 'None' that
            # that applies to all keys.

            if len(arg) == 1 and None in dict:
                layers.append('dict*')

                self._validate_arg(arg[None], layers)
            elif None in dict:
                layers.append('dict[None]')
                raise ArgTypeError(
                    "A dict type was given with multiple defined keys as well "
                    "as None. It can only be one or the other.",
                    layers=layers
                )
            else:
                for key, val in arg.items():
                    key_layers = layers.copy()
                    key_layers.append('dict[{}]'.format(key))
                    if not isinstance(key, str):
                        raise ArgTypeError(
                            "Dictionary keys must be a string.",
                            layers=layers
                        )

                    self._validate_arg(val, key_layers)

        elif not callable(arg):
            layers.append(repr(arg))
            raise ArgTypeError(
                "Except for lists or mappings, arg types must be a callable "
                "(that takes a single argument), got {}"
                .format(arg),
                layers=layers
            )

        # Everything else is ok.

    def __call__(self, *args):
        """
        :param args:
        :return:
        """

        args = []

        for i in range(len(args)):
            arg_type = self.arg_types[i]
            try:
                args.append(self._apply_type(args[i], arg_type))
            except ArgTypeError as err:
                raise

        ret_val = self._run(args)

        try:
            ret_val = self._apply_type(ret_val)
        except ArgTypeError as err:
            raise

    def _apply_type(self, arg, arg_type):
        if isinstance(arg_type, list):



    def _run(self, args):
        raise NotImplementedError


    @property
    def path(self):
        """The path to the file containing this result parser plugin."""

        return inspect.getfile(self.__class__)

