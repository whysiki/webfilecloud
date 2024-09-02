git push origin --delete async
git push origin --delete master
git push origin --delete card
git add .
git commit -m "fix: remove branch"
git push -f
git push origin --delete refs/heads/profile
git push origin --delete refs/tags/profile

@REM 删除跟踪
git rm --cached vue_interface\src\axios.js 
git commit -m "Stop tracking axios.js"
echo "vue_interface\src\axios.js " >> .gitignore
git add .gitignore
git commit -m "Update .gitignore"

git tag miniov1

git push origin miniov1

git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch other/minio_storage/minio.exe' --prune-empty --tag-name-filter cat -- --all

git filter-repo --path minio.exe --invert-paths

