# Creating a New GitHub Repository and Pushing Your Code

Follow these steps to create a new GitHub repository and push your code to it:

## Step 1: Create a New Repository on GitHub

1. Go to [GitHub](https://github.com/) and log in to your account
2. Click on the "+" icon in the top-right corner and select "New repository"
3. Enter a name for your repository (e.g., "azure-pdf-extraction")
4. Optionally add a description (e.g., "PDF text extraction using Azure Document Intelligence and OpenAI")
5. Choose the repository visibility (Public or Private)
6. Do NOT initialize the repository with any files (no README, no .gitignore, no license)
7. Click "Create repository"

## Step 2: Push Your Local Repository to GitHub

After creating the repository, GitHub will show instructions for pushing your existing repository. Follow the instructions for "...or push an existing repository from the command line".

Copy and paste these commands in your terminal:

```bash
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
git branch -M main
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username and `YOUR-REPO-NAME` with the name of your repository.

## Step 3: Verify Your Code is on GitHub

1. Refresh the GitHub page
2. You should now see all your files in the repository

## Step 4: Future Updates

For future changes:

```bash
# Make changes to your code
# Add the changes to Git
git add .

# Commit the changes
git commit -m "Description of the changes"

# Push the changes to GitHub
git push
```
