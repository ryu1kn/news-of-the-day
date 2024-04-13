
# Infra

This is the infrastructure code for this project.

## Prerequisites

* Python 3.12 is installed

## Setup

1. Create a virtual environment, and activate it

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

1. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

## Usage

Refer to the output of `cdk help`. The instruction for cdk is provided
in [cdk.json](./cdk.json).

For example, to deploy the stack, run:

```bash
# Make sure correct AWS profile and region is specified
cdk deploy
```
