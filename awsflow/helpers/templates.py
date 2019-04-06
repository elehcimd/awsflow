import copy

from awsflow.helpers.log import fatal, logger

logging = logger.setup()


class Templates:
    """
    Class that maintains a global list of registered EMR templates
    """

    def __init__(self):
        self.templates = {}

    def register(self, template):
        """
        Register new template
        :param template: dict defining a complete template
        :return:
        """
        assert template['Name'] not in self.templates
        self.templates[template['Name']] = template

    def get_names(self):
        """
        Get list of template names
        :return: list of template names
        """
        return [t['Name'] for t in self.templates.values()]

    @classmethod
    def assign_params(cls, t, params):
        """
        Assigns parameters inside the template, visiting recursively dicts and lists.
        E.g., occurrences of '{date}' are substituted with the value of params['date'].
        :param t: template
        :param params: dictionary { 'param_name' : 'param_value'}
        :return:
        """

        def f(t):
            """
            Subtitutes {param_name} occurrences with param value
            :param t: template
            :return:
            """
            if type(t) in [dict, list]:
                cls.assign_params(t, params)
                return t
            elif callable(t):
                return t(**params)
            else:
                # apply format only if string
                return t.format(**params) if type(t) is str else t

        if type(t) == dict:
            for k in t:
                t[k] = f(t[k])
        elif type(t) == list:
            for i in range(len(t)):
                t[i] = f(t[i])
        elif callable(t):
            f(t)

    def get(self, name, params=[]):
        """
        Get template, applying params and func

        An attempt is made to parse intergers, this is done so that formatting
        parameters for zero passing can be used in the templates. Useful for
        dealing with inconsistent date formatting.
        :param name: name of template to retrieve
        :param params: list of strings 'name:value' applied to all strings in template
        :return: dict of selected template
        """

        if name not in self.templates:
            fatal("Template '{}' not found".format(name))

        t = copy.deepcopy(self.templates[name])

        dict_params = {}
        if params:
            for param in params:
                key, value = param.split('=')
                try:
                    value = int(value)
                except ValueError:
                    pass
                dict_params[key] = value

            logging.info('Template parameters: {}'.format(dict_params))

        try:
            Templates.assign_params(t, dict_params)
        except KeyError as keyError:
            fatal("Missing template parameter: {}".format(keyError))

        return t
