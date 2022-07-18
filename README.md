# FSU Classbot 3.0

Time for a revamp! Gonna design it from the ground up with Docker in mind.

## To-Do Checklist

- [x] Get the script working :)
- [x] Discord integration
- [ ] Browserless integration
- [x] Docker support

## Environment Variables

| Variable | Req? | Default | Values | Description |
|:--------:|:--------:|:-------:|:-------|:------------|
| `FSU_USERNAME`    | Yes | None | `<FSUID>` | The username used to log into FSU CAS
| `FSU_PASSWORD`    | Yes | None | `<password>` | The password used to log into FSU CAS
| `FSU_SEMESTER`    | Yes | None | `<"spring"\|"summer"\|"fall">` | The desired semester to use for class enrollment
| `DISCORD_URL`     | Yes | None | `<URL>` | The discord webhook URL you'd like to send notifications to
| `DISCORD_PINGS`   | No  | None | `<List of escaped tags>` | The tags you'd like to be included before any discord embeds sent (e.g. `"<@!123456789012345678>"`)
| `DRIVER`          | Yes | `firefox` | `<"firefox"\|"browserless">` | The driver you'd like to use (Note: Browserless is a service, not a free choice!)
| `DRIVER_HEADLESS` | No  | `True` | `<"true"\|"false">` | If using a local driver, (e.g. `firefox`) this sets whether you want to see the browser as it works
| `DRIVER_URL`      | No  | None | `<URL>` | If using Browserless, this is the URL of the server you'd like to connect to. This is passed into `selenium.Remote()`
| `DRIVER_TIMEOUT`  | No  | `15` | `<int>` | The number of seconds for the WebDriver to wait for expected conditions (e.g. `element_to_be_clickable`)
| `DRIVER_SLEEP`    | No  | `2`  | `<int>` | The number of seconds to wait before looping
