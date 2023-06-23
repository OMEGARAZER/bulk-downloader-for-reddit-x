if ((-not ([string]::IsNullOrEmpty($env:REDDIT_CLIENT))) -and (-not ([string]::IsNullOrEmpty($env:REDDIT_TOKEN))))
{
    Copy-Item .\\bdfrx\\default_config.cfg .\\tests\\test_config.cfg
    (Get-Content -ReadCount 0 .\\tests\\test_config.cfg) -replace "client_id =", "" | ? {$_.trim() -ne "" } | Set-Content .\\tests\\test_config.cfg
    Write-Output "`nclient_id = $env:REDDIT_CLIENT`nuser_token = $env:REDDIT_TOKEN" >> ./tests/test_config.cfg
}
