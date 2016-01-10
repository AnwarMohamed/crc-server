## CRC-Project Webservice API

### Virtual Machines
---
#### Start a virtual machine on a given node name
```
POST 	/api/v1/vm/{node_name}/start
Authorization: Basic {basic_auth}
```
1. `node_name` is the name of the selected node to start the vm on.

##### Returns
1. `200` request was processed successfully.
2. `400` invalid `node_name`.
3. `401` invalid authentication credentials.

#### Stop a virtual machine on a given node name
```
POST	/api/v1/vm/{node_name}/stop
Authorization: Basic {basic_auth}
```
1. `node_name` is the name of the selected node to stop the vm on.

##### Returns
1. `200` request was processed successfully.
2. `400` invalid `node_name`.
3. `401` invalid authentication credentials.

#### Reset a virtual machine on a given node name
```
POST	/api/v1/vm/{node_name}/reset
Authorization: Basic {basic_auth}
```
1. `node_name` is the name of the selected node to reset the vm on.

##### Returns
1. `200` request was processed successfully.
2. `400` invalid `node_name`.
3. `401` invalid authentication credentials.

#### Get status of virtual machine on a given node name
```
GET		/api/v1/vm/{node_name}/status
Authorization: Basic {basic_auth}
```
1. `node_name` is the name of the selected node to get the status of the vm on.

##### Returns
1. `400` invalid `node_name`.
2. `401` invalid authentication credentials.
3. `200` request succeeded. The structure below is returned.
```
{
	'status': '{on/off}'
}
```

### Imaging
---
#### Load an image to a given list of nodes
```
POST	/api/v1/image/load
Authorization: Basic {basic_auth}
{
	'name': 'image_name',
    'path': 'image_path',
    'node_list': []
}
```
1. `name` is the name of the selected image to be loaded on the nodes.
2. `path` is the path of the selected image to be loaded on the nodes.
3. `node_list` is list of nodes to load the image on.

##### Returns
1. `400` invalid `name` or `path` or `node_list`.
2. `401` invalid authentication credentials.
3. `200` request succeeded. The structure below is returned.
```
{
	'task_id': '{load_task_id}'
}
```

#### Check load status of a given {load\:task_id}
```
GET		/api/v1/image/load/{task_id}
Authorization: Basic {basic_auth}
```
1. `task_id` is a load task id of an image.

##### Returns
1. `400` invalid `task_id`.
2. `401` invalid authentication credentials.
3. `200` request succeeded. The structure below is returned.
```
{
	'task_id': '{task_id}',
    'percentage': {%},
    'error': {true/false}
}
```
#### Save the images of a given list of nodes
```
POST	/api/v1/image/save
Authorization: Basic {basic_auth}
{
	'name': 'image_name',
    'path': 'image_path',
    'node_list': []
}
```
1. `name` is the name of the image to be saved.
2. `path` is the path of the image to be saved.
3. `node_list` is list of nodes to save the image from.

##### Returns
1. `400` invalid `name` or `path` or `node_list`.
2. `401` invalid authentication credentials.
3. `200` request succeeded. The structure below is returned.
```
{
	'task_id': '{save_task_id}'
}
```

#### Check save status of a given {save\:task_id}
```
GET		/api/v1/image/save/{task_id}
Authorization: Basic {basic_auth}
```
1. `task_id` is a save task id of an image.

##### Returns
1. `400` invalid `task_id`.
2. `401` invalid authentication credentials.
3. `200` request succeeded. The structure below is returned.
```
{
	'task_id': '{task_id}',
    'percentage': {%},
    'error': {true/false}
}
```
