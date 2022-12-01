if (Test-Path -Path $args[0] -PathType Leaf) {
    $file=$args[0]
}
else {
    Write-Host "CANNOT FIND LOG FILE"
    Exit 1
}

if ($null -ne $args[1]) {
    $output=$args[1]
    Write-Host "Outputting IDs to $output"
}
else {
    $output="./successful.txt"
}

Select-String -Path $file -Pattern "Downloaded submission" | ForEach-Object { -split $_.Line | Select-Object -Last 3 | Select-Object -SkipLast 2 } >> $output
Select-String -Path $file -Pattern "Resource hash" | ForEach-Object { -split $_.Line | Select-Object -Last 3 | Select-Object -SkipLast 2 } >> $output
Select-String -Path $file -Pattern "Download filter" | ForEach-Object { -split $_.Line | Select-Object -Last 4 | Select-Object -SkipLast 3 } >> $output
Select-String -Path $file -Pattern "already exists, continuing" | ForEach-Object { -split $_.Line | Select-Object -Last 4 | Select-Object -SkipLast 3 } >> $output
Select-String -Path $file -Pattern "Hard link made" | ForEach-Object { -split $_.Line | Select-Object -Last 1 } >> $output
