# ansible-viptela


An Ansible Role for automating a Viptela Overlay Network

This role can perform the following functions:
- Add Controllers
- Set Organization Name
- Set vBond
- Set Enterprise Root CA
- Get Controller CSR
- Install Controller Certificate
- Install Serial File

## Examples


Add vBond Host:
```yaml
    - name: Add vBond Hosts
      include_role:
        name: ansible-viptela
        tasks_from: add-controller
      vars:
        device_hostname: "{{ item }}"
        device_ip: "{{ hostvars[item].transport_ip }}"
        device_personality: vbond
      loop: "{{ groups.vbond_hosts }}"
```

Add vSmart Host:
```yaml
    - name: Add vSmart Hosts
      include_role:
        name: ansible-viptela
        tasks_from: add-controller
      vars:
        device_hostname: "{{ item }}"
        device_ip: "{{ hostvars[item].transport_ip }}"
        device_personality: vsmart
      loop: "{{ groups.vsmart_hosts }}"
```

Set Organization:
```yaml
    - name: Set organization
      include_role:
        name: ansible-viptela
        tasks_from: set-org
      vars:
        org_name: "{{ organization_name }}"
```

Set vBond:
```yaml
    - name: Set vBond
      include_role:
        name: ansible-viptela
        tasks_from: set-vbond
      vars:
        vbond_ip: "{{ hostvars[vbond_controller].transport_ip }}"
```

Set Enterprise Root CA:
```yaml
    - name: Set Enterprise Root CA
      include_role:
        name: ansible-viptela
        tasks_from: set-rootca
      vars:
        root_cert: "{{lookup('file', '{{ viptela_cert_dir }}/myCA.pem')}}"
```

Get Controller CSR:
```yaml
    - name: Get Controler CSR
      include_role:
        name: ansible-viptela
        tasks_from: get-csr
      vars:
        device_ip: "{{ hostvars[item].transport_ip }}"
        device_hostname: "{{ item }}"
        csr_filename: "{{ viptela_cert_dir }}/{{ item }}.{{ env }}.csr"
      loop: "{{ groups.viptela_control }}"
```

Installing Controller Certificates:
```yaml
    - name: Install Controller Certificate
      include_role:
        name: ansible-viptela
        tasks_from: install-cert
      vars:
        device_cert: "{{lookup('file', '{{ viptela_cert_dir }}/{{ item }}.{{ env }}.crt')}}"
      loop: "{{ groups.viptela_control }}"
```

Installing Serial File:
```yaml
    - name: Install Serial File
      include_role:
       name: ansible-viptela
       tasks_from: install-serials
      vars:
       viptela_serial_file: 'licenses/viptela_serial_file.viptela'
```

License
-------

CISCO SAMPLE CODE LICENSE