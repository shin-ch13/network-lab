schema = '''
type: map
mapping:
 "networks":
    type: map
    mapping:
      "=":
        type: map
        mapping:
          "desc":
            type: str
          "conn":
            type: str
            enum: ['direct', 'bridge']
            required: True
          "members":
            type: seq
            sequence:
              - type: map
                required: True
                mapping:
                  "name":
                    type: str
                    required: True
                  "iface":
                    type: str
                    required: True
                  "ip":
                    type: seq
                    sequence:
                      - type: str
                        unique: True
 "commands":
    type: map
    mapping:
      "=":
        type: seq
        sequence:
          - type: map
            required: True
            mapping:
              "cmd":
                type: str
                required: True
'''