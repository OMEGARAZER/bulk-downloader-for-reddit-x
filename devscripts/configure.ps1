if (-not ([string]::IsNullOrEmpty($env:REDDIT_TOKEN)))
{
    Copy-Item .\\bdfr\\default_config.cfg .\\test_config.cfg
    Write-Output "`nuser_token = $env:REDDIT_TOKEN" >> ./test_config.cfg
}
