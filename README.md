How to start clone repo with git clone [https://github.com/artemdev/PhotoSharingApp.git](https://github.com/artemdev/PhotoSharingApp.git)

***HOW TO RUN SERVER*** <br /> <br />
Navigate to the server folder with ```cd ./server```

Add ```.env``` file (from slack) 

Create all services with ```docker-compose up -d```

Run virtual env with ```poetry shell```
Install dependencies with ```poetry install```
Apply migrations with ```alembic upgrade head```

Create a new branch from main with ```git checkout -b 'feature-name'```

***HOW TO RUN CLIENT*** <br /> <br />
```cd ./client```
Install npm on your local machine
```npm install```
```npm run dev```


Enjoy and have fun! :)
