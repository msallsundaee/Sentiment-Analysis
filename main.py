"""CLI for the sentiment-analysis project.

  python main.py scrape [--limit N] [--facebook]
                                      Task 1: data/posts.csv -> data/raw/raw_comments.csv (YouTube/Reddit APIs)
  python main.py analyze              Tasks 2-4: translate, preprocess, lexicons, ML
  python main.py deck [--section X]   Task 6: results/Sentiment_Analysis_Inflation.pptx
"""
import argparse


def analyze():
    from src import config, lexicon, ml, preprocess, translate
    df = preprocess.load_raw()
    df["text_en"] = translate.translate_all(df.text.tolist())
    df["cleaned"] = df.text_en.map(preprocess.clean)
    df[["text", "text_en", "cleaned", "timestamp", "platform"]].to_csv(config.CLEANED, index=False)
    df = lexicon.score(df)
    df.to_csv(config.LEXICON, index=False)
    lexicon.plot_distribution(df)
    print(ml.run(df))
    if config.SHEET.exists():
        from src import collect
        collect.sync_sheet(df)
    from src import visualize_more
    visualize_more.plot_all()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sc = sub.add_parser("scrape")
    sc.add_argument("--limit", type=int, default=400, help="max comments per post")
    sc.add_argument("--facebook", action="store_true", help="also scrape Facebook links in a browser (opt-in)")
    sub.add_parser("import-sheet", help="rebuild raw_comments.csv from the group sheet, stripping @handles")
    sub.add_parser("analyze")
    dk = sub.add_parser("deck")
    dk.add_argument("--section", default="CS412")
    dk.add_argument("--instructor", default="________")
    a = ap.parse_args()
    if a.cmd == "scrape":
        from src import collect
        collect.run(a.limit, a.facebook)
    elif a.cmd == "import-sheet":
        from src import collect
        collect.import_sheet()
    elif a.cmd == "analyze":
        analyze()
    else:
        from src import deck
        print("saved deck,", deck.build(a.section, a.instructor), "slides")


if __name__ == "__main__":
    main()
