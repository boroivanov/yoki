task_digest_items = [
    {
        "cluster": "test-yoki",
        "createdAt": "2019-06-07T18:32:38.003Z",
        "definition": "test-yoki-srv1:43",
        "deployment": "ecs-svc/9223370476922431730",
        "desiredCount": 2,
        "images": [
            "srv1_image:cbc7322",
            "nginx"
        ],
        "launchType": "FARGATE",
        "pendingCount": 0,
        "runningCount": 2,
        "service": "srv1",
        "tasks": {
            "76a65c984b3f4b46bb96b39da37e9483": "RUNNING",
            "f37775e7b4214a0a8c96045ed46642e2": "RUNNING"
        },
        "TTL": 1562524359,
        "updatedAt": "2019-06-07T18:32:38.003Z"
    },
    {
        "cluster": "staging",
        "createdAt": "2019-05-15T17:15:29.176Z",
        "definition": "test-yoki-srv2:13",
        "deployment": "ecs-svc/9223370478914266237",
        "desiredCount": 0,
        "images": [
            "srv2_image:master"
        ],
        "launchType": "FARGATE",
        "pendingCount": 0,
        "runningCount": 0,
        "service": "srv2",
        "tasks": {
            "2f95b10a7c634b9abd0ad44f9782017f": "STOPPED",
            "8413fd3dd536436b8e2af2d13bff7ef6": "STOPPED"
        },
        "TTL": 1560532536,
        "updatedAt": "2019-05-15T17:15:29.176Z"
    },
    {
        "cluster": "test-yoki",
        "createdAt": "2019-05-15T17:15:29.176Z",
        "definition": "test-yoki-srv2:13",
        "deployment": "ecs-svc/9223370478914266236",
        "desiredCount": 0,
        "images": [
            "srv2_image:srv2"
        ],
        "launchType": "FARGATE",
        "pendingCount": 0,
        "runningCount": 2,
        "service": "srv2",
        "tasks": {
            "2f95b10a7c634b9abd0ad44f9782017f": "RUNNING",
            "8413fd3dd536436b8e2af2d13bff7ef6": "RUNNING"
        },
        "TTL": 1560532536,
        "updatedAt": "2019-05-15T17:15:29.176Z"
    }
]
