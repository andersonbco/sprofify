import configargparse


def get_options():

    p = configargparse.ArgParser(default_config_files=["~/.config/sprofify.config"])
    p.add_argument("--config", "-c", is_config_file=True, help="config file path")
    p.add_argument("--username", "-u", help="spotify username")
    p.add_argument("--client_id", help="spotify client id")
    p.add_argument("--client_secret", help="spotify client secret")
    p.add_argument(
        "--device_type",
        help="Name of the device used to play the songs",
        choices=["Computer", "Smartphone"],
        default="Computer",
    )

    return p.parse_args()
