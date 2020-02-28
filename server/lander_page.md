# API Lander page

***

## Generate path map images
```
/pathgenerator
```

### Parameters

| Name          | Type      | Description |
|---------------|-----------|-------------|
| `username`    | `string`  | **Required.** Username of player |
| `start_time`  | `int`     | **Required.** Unix timestamp of start time |
| `end_time`    | `int`     | **Required.** Unix timestamp of end time |
| `gen_empty`   | `bool`    | Whether or not to generate empty images with no interaction. Default: `false` |