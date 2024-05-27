How to start clone repo with git clone [https://github.com/artemdev/PhotoSharingApp.git](https://github.com/artemdev/PhotoSharingApp.git)

***HOW TO RUN SERVER*** <br /> <br />
Navigate to the server folder with ```cd ./server```

1. Add ```.env``` file (from slack)
2. Create all services with ```docker-compose up -d```
3. Run virtual env with ```poetry shell```
4. Install dependencies with ```poetry install```
5. Apply migrations with ```alembic upgrade head```

Create a new branch from main with ```git checkout -b 'feature-name'```

***HOW TO RUN CLIENT*** <br /> <br />
```cd ./client```
1. Install npm on your local machine
2. ```npm install```
3. ```npm run dev```




Enjoy and have fun! :)
