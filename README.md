

# Dotbot apt-get plugin

Supports a customizable install workflow.

Goal is to make this python2 and python3 compliant

```yaml
- apt-get:
    options:
      bail: False
    workflows:
      - set0:
          update: True
          packages:
            - gpg
            - apt-transport-https
      - set1:
          custom:
          - wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
          - install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
          - echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list
          - rm -f packages.microsoft.gpg
      - set2:
          update:
            True
          custom:
            - echo "Hello World"
          packages:
            - linux-headers-$(uname -r)
            - code
            - vim
            - htop
            - nmap
            - tig
            - python2
            - gparted
            - build-essential
```