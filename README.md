

# Dotbot apt-get plugin

Supports a customizable install workflow.

Goal is to make this python2 and python3 compliant

```yaml
- apt-get:
    options:
      bail: False
    workflows:
      - setup_apt_for_vscode:
          update: True
          packages:
            - gpg
            - apt-transport-https
      - add_microsoft_to_sources_list:
          bash:
          - wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
          - install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
          - echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list
          - rm -f packages.microsoft.gpg
      - install_main_packages:
          update:
            True
          bash:
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