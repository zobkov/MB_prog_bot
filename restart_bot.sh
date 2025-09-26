#!/bin/bash
systemctl daemon-reload
systemctl restart mb_alumni_bot
journalctl -u mb_alumni_bot.service -f