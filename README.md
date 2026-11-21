# Sum up 20 November's world news in one image

Entry for the make.fun bounty
“Sum up 20 November's world news in one image”
(https://make.fun/bounty/news-image-20261120).

## What it is

`main.py` (Python 3.13, standard library only, no network) writes one
1024x1024 PNG summarising six world-news stories from 20 November 2026:

- Shenzhen: Trump, Xi and Putin hold their first three-way summit
- The Hague: ICJ rules Myanmar committed genocide against the Rohingya
- Kyiv / Poland: Russia strikes Kyiv, missiles land in Poland
- Markets: stocks fall for a fifth day, Nikkei down 4.8%
- Riyadh: Houthi missiles hit a Riyadh tower
- Antalya: COP31 draft drops the fossil-fuel phase-out call

## Run

```sh
python3 main.py
```

It writes `entry.png` next to `main.py` (or to `/output/entry.png`
when `/output` exists). Running it twice writes identical bytes.

## License

MIT — see `LICENSE`.
