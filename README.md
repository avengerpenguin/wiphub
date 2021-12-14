# Wiphub

Wiphub is a semi-automated workflow assistant for managing "work in progress" (WIP) on Github.

## Running

As the workflow is baked in and opinionated (see workflow below), the only
input needed before running the command is your Github token:

```bash
# export GITHUB_TOKEN=<secret goes here>
# wip
```

## Workflow

The workflow is fixed in order to follow some Kanban-inspired rules, but over
time it may be possible to make this somewhat configurable. It should be noted
that fully configurability would detract from the purpose which is:

1. The machine should do as much work for you as it can
2. A linear work order is preferred to remove decisions and analysis paralysis
   from your daily work

That is, when between "deep work" tasks, it should be possible to run `wip`
without overthinking what it should do and let it walk you through things that
need finishing or cleaned up.

The workflow order currently is:

### 1. Clear down notifications

Notifications are part inbox, part indication you might be blocking some work.
With the latter consideration in mind, the preferred first step in Wiphub's
automated workflow is clear these down.

#### 1a. Clear for closed issues

Where a pull request or issue is now closed, simply clear the notification.
You have likely missed the window to contribute, but the closed issue is
printed to the console just in case you wish to go check the reason why it's
closed perhaps.
