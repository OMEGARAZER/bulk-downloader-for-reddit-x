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
    $output="./failed.txt"
}

Select-String -Path $file -Pattern "Could not download submission" | ForEach-Object { -split $_.Line | Select-Object -Skip 11 | Select-Object -First 1 } | ForEach-Object { $_.substring(0,$_.Length-1) } >> $output
Select-String -Path $file -Pattern "Failed to download resource" | ForEach-Object { -split $_.Line | Select-Object -Skip 14 | Select-Object -First 1 } >> $output
Select-String -Path $file -Pattern "failed to download submission" | ForEach-Object { -split $_.Line | Select-Object -Skip 13 | Select-Object -First 1 } | ForEach-Object { $_.substring(0,$_.Length-1) } >> $output
Select-String -Path $file -Pattern "Failed to write file" | ForEach-Object { -split $_.Line | Select-Object -Skip 13 | Select-Object -First 1 } >> $output
Select-String -Path $file -Pattern "skipped due to disabled module" | ForEach-Object { -split $_.Line | Select-Object -Skip 8 | Select-Object -First 1 } >> $output
