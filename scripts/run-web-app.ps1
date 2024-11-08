$imageName = "personal-finance-for-newbies"

$exists = docker images -q $imageName

if (-not $exists) {
    Write-Host "The image does not exist. Building it now..."
    docker build -t $imageName .
} else {
    Write-Host "The image '$imageName' already exists, the app is running at http://localhost:8080"
}

docker run --rm -p 8080:8501 $imageName