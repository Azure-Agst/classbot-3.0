# Classbot 3.0

<!-- TODO: 
    Badges go here, once the project goes public.
    Use https://shields.io :)
-->

Tired of admitting defeat when the last class for your perfect schedule is already full? Classbot can help.

Classbot is a Python & Selenium powered web bot that can be used to help you swipe up enrollments in your desired classes within seconds of them becoming available. Just put your desired classes into your cart and let Classbot do the rest! Enrollment day and Drop/Add have never been easier!

## Usage

### Option 1.) Docker

Docker is the preferred means of running the bot. It's as simple as putting your desired config in a `.env` file and running the following on a machine with Docker installed. See the [env var reference](#environment-variables) below for help.

```bash
docker compose up -d
```

Optionally if you don't wish to clone the entire repo to get this to work, use the published images on GitHub's Container Registry! We have another compose file that does just that:

```bash
docker compose up -df docker-compose-prod.yml
```

### Option 2.) Firefox

Clone the repo to your machine and ensure you have Firefox installed. You'll also need [Geckodriver](https://github.com/mozilla/geckodriver/releases) somewhere in your path. Personally, I just drop the executable in this folder and python finds it just fine.

Once that's all set, make a virtualenv and install dependencies:

```bash
$ python3 -m venv .venv
$ source .venv/bin/bash
$ pip install -r requirements.txt
```

Make a `.env` file and put your configuration into it. See the [env var reference](#environment-variables) below for help.

Finally, run the `classbot` module:

```bash
python3 -m classbot
```

## Environment Variables

| Variable | Req? | Default | Values | Description |
|:--------:|:--------:|:-------:|:-------|:------------|
| `FSU_USERNAME`    | Yes | None | `<FSUID>` | The username used to log into FSU CAS
| `FSU_PASSWORD`    | Yes | None | `"<password>"` | The password used to log into FSU CAS (NOTE: Escape with quotes!)
| `FSU_SEMESTER`    | Yes | None | `<"spring"\|"summer"\|"fall">` | The desired semester to use for class enrollment
| `DISCORD_URL`     | Yes | None | `<URL>` | The discord webhook URL you'd like to send notifications to
| `DISCORD_PINGS`   | No  | None | `<List of escaped tags>` | The tags you'd like to be included before any discord embeds sent (e.g. `"<@!123456789012345678>"`)
| `DISCORD_MODULO`  | No  | `5`  | `<int>` | The number of loops to wait between updating the webhook (i.e. Rate limit avoidance)
| `DRIVER`          | Yes | Depends | `<"firefox"\|"docker">` | The driver you'd like to use. Docker images use `docker` by default, but there's no default otherwise.
| `DRIVER_HEADLESS` | No  | `True` | `<"true"\|"false">` | If using a local driver, (e.g. `firefox`) this sets whether you want to see the browser as it works
| `DRIVER_URL`      | No  | None | `<URL>` | If using Browserless, this is the URL of the server you'd like to connect to. This is passed into `selenium.Remote()`
| `DRIVER_TIMEOUT`  | No  | `15` | `<int>` | The number of seconds for the WebDriver to wait for expected conditions (e.g. `element_to_be_clickable`)
| `DRIVER_SLEEP`    | No  | `2`  | `<int>` | The number of seconds to wait before looping

## Frequently Asked Questions

### How does Classbot work?

At a basic level: Classbot uses a library called Selenium, which works allows you to control special instances of web browsers using code. Classbot builds on top of that by using selenium to automate your enrollment process.

### Why a whole browser? Why not just use `requests`?

My college's enrollment portal is way too complex to be "emulated" without spending hours upon hours doing research and testing. I'm lazy. Scripting was simpler. Plus it looks like an actual browser on their end, rather than a pretty obvious bot.

### Is botting the enrollment system even allowed?

Idk. Depends.

At least for FSU, the only thing I could find on the matter is [Policy 4-OP-H-5](https://policies.vpfa.fsu.edu/policies-and-procedures/technology/information-security-policy), Section II.C, Subheading "Personal Use", Clause 1:

> Personal use of University IT resources must not consume significant amounts of IT resources (e.g., bandwidth, storage)

The only innapropriate use case that might apply can be found in the same policy and section, Subheading "Innapropriate Use", Clause 2:

> Members may not use University IT resources for [...] any activity which may adversely affect the confidentiality, integrity, or availability of IT resources or data.

Arguably, the only way that this bot could really be argued against is the fact that it's consuming a constant non-zero amount of bandwidth, which could affect service availability. But then again, the bot isn't flooding the server with nearly enough info to be considered a DoS attack, which is really what that clause is intended for.

No clear-cut rules here. Your fate is ultimately up to sysadmin discretion if/when they detect that you're botting.

**TL;DR:** Tread at your own peril.

## Contributing

Contributions to the project, once it gets published, will be accepted so long as all proposed changes are done on a separate branch and don't break the code. "Breaking the code" is a loose definition, as I don't have a testing suite yet, nor do I really feel like setting one up at the moment. Lord knows how I'd go about it, anyway.

For now all changes have to be approved by @Azure-Agst before being merged in.

I'll establish actual contributing guidelines later.

## License

This project is licensed under the GNU General Public License v3.0. Full license text can be found in the [LICENSE](./LICENSE) file.
