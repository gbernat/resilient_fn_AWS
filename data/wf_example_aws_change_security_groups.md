<!--
    DO NOT MANUALLY EDIT THIS FILE
    THIS FILE IS AUTOMATICALLY GENERATED WITH resilient-circuits codegen
-->

# Example: AWS Change Security Groups

## Function - AWS: EC2 modify security groups

### API Name
`aws_ec2_modify_security_groups`

### Output Name
``

### Message Destination
`fn_aws`

### Pre-Processing Script
```python
inputs.aws_resource_id = artifact.value
inputs.aws_security_groups = 'sg-032bea0e7926abfbc,sg-01e6a74a8527336bb'
```

### Post-Processing Script
```python
if results.success:
  incident.addNote('Security Groups for Instance: {} were successfully changed.'.format(artifact.value))
```

---

