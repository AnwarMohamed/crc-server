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
	'status': 'on/off'
}
```
