API for adding Swift as a service in Tsuru, implemented using Flask (Python).

##User

Considering you are using a pre-configured Tsuru cloud and that Swiftsuru is already available, you will be able to:

###Check which Swift plans are available

	tsuru service-info swift
	
###Create a new Swift instance

	tsuru service-add swift <swift-instance-name> <swift-plan>
	
###Bind your swift instance to an existing app

	tsuru bind <swift-instance-name> --app <app-name>
	
After binding, the following environment variables will be available at your App units:

* SWIFT\_ADMIN\_URL
* SWIFT\_AUTH\_URL
* SWIFT\_CONTAINER
* SWIFT\_INTERNAL\_URL
* SWIFT\_PASSWORD
* SWIFT\_PUBLIC\_URL
* SWIFT\_TENANT
* SWIFT\_USER

There are some possible use cases to integrate your App with Swift. The most common use case is deploy/serve the static file of your application. To easily do this, we recommend [simple-swifclient](https://github.com/globocom/simple-swiftclient).

Example of deploy hook of a Django App.

tsuru.yml
```
hooks:
    build:
        - bash /home/application/current/static-deploy-hook.sh
```

static-deploy-hook.sh

```
#!/bin/bash
python manage.py collectstatic --noinput && \
cd /home/application/current && \
simpleswift --os-auth-url $SWIFT_AUTH_URL \
            --os-username $SWIFT_USER \
            --os-password $SWIFT_PASSWORD \
            --os-tenant-name $SWIFT_TENANT \
            upload $SWIFT_CONTAINER <static_root>
```

##Developers

###How to run


In order to install dependencies and run the Swiftsuru API locally, do:

```
make setup
make run
```

###How to run tests

    make tests
