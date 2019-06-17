# SAM-IAM

Hmm, so you want to be federated!

# Install Steps

## Step 1. Pre-requirements

1. Requires Chrome V71 and above. Use (https://www.whatismybrowser.com/)
2. Requires python 3.6 or above

## Step 2. Installation

### Installation via clone

1. Clone the repository
2. Then run the following command:

```bash
pip install . --user
```

### Installation via tag

```bash
pip install -e git://github.com/tsriharsha/sam-iam.git@<release-tag>#egg=sam
```

## Step 3. Run the configure command

Run the following command:

```bash
sam configure
```  

# Help Commands

```bash
sam --help
sam configure --help
sam iam --help
sam iam get-creds --help
sam iam refresh --help
```


# Fetch Creds

Run the following command:

```bash
sam iam get-creds -d -e
```



