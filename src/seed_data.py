"""Generate realistic seed comments for Philippine inflation & cost of living topic.
Allows running Tasks 2-4 and Task 6 immediately without waiting for API keys.
"""
import csv
import json
from src import config

SEED_COMMENTS = [
    # Negative comments (frustrated, complaining about high prices)
    ("Sobrang mahal na ng bilihin ngayon, lalo na ang bigas at sibuyas. Hindi na kasya ang sahod.", "2026-03-01", 45, "youtube", "https://youtube.com/watch?v=sample1", "Groceries are so expensive now, especially rice and onions. Salary is no longer enough."),
    ("Gasoline prices went up again for the third consecutive week. Commuters and drivers suffer the most.", "2026-03-02", 120, "reddit", "https://reddit.com/r/Philippines/sample2", "Gasoline prices went up again for the third consecutive week. Commuters and drivers suffer the most."),
    ("Grabe ang taas ng kuryente at tubig ngayon buwan! Halos kalahati ng kita napupunta lang sa bills.", "2026-03-03", 88, "youtube", "https://youtube.com/watch?v=sample1", "Electricity and water bills are terribly high this month! Almost half the income goes straight to bills."),
    ("Every grocery run feels depressing. A thousand pesos buys almost nothing compared to two years ago.", "2026-03-03", 215, "reddit", "https://reddit.com/r/Philippines/sample2", "Every grocery run feels depressing. A thousand pesos buys almost nothing compared to two years ago."),
    ("Wala na ngang maipon, baon pa sa utang dahil sa walang tigil na pagtaas ng presyo.", "2026-03-04", 67, "youtube", "https://youtube.com/watch?v=sample1", "Cannot save anything anymore, even drowning in debt because of the nonstop price hikes."),
    ("The inflation rate might be statistically lower on paper, but on the ground in markets, prices are insane.", "2026-03-05", 143, "reddit", "https://reddit.com/r/Philippines/sample2", "The inflation rate might be statistically lower on paper, but on the ground in markets, prices are insane."),
    ("Pahirap talaga sa mahihirap itong walang tigil na pagmahal ng pamasahe at pagkain.", "2026-03-06", 92, "youtube", "https://youtube.com/watch?v=sample1", "It's really hard on the poor with this nonstop increase in fares and food."),
    ("Student living allowance cannot cope with canteen and dormitory rent increases anymore.", "2026-03-06", 76, "reddit", "https://reddit.com/r/Philippines/sample2", "Student living allowance cannot cope with canteen and dormitory rent increases anymore."),
    ("Kahit anong tipid gawin mo, kakainin lang ng inflation ang anumang naipon.", "2026-03-07", 54, "youtube", "https://youtube.com/watch?v=sample1", "No matter how much you save, inflation will just eat up whatever you have saved."),
    ("Meat and vegetable vendors are also struggling because customers are buying less.", "2026-03-07", 34, "reddit", "https://reddit.com/r/Philippines/sample2", "Meat and vegetable vendors are also struggling because customers are buying less."),
    ("Nakakalungkot ang kalagayan ng minimum wage earners. Hindi makatarungan ang presyo ng bigas.", "2026-03-08", 110, "youtube", "https://youtube.com/watch?v=sample1", "The condition of minimum wage earners is sad. The price of rice is unfair."),
    ("Skipping meals just to budget for rent and transport is becoming normal for young workers.", "2026-03-08", 89, "reddit", "https://reddit.com/r/Philippines/sample2", "Skipping meals just to budget for rent and transport is becoming normal for young workers."),
    ("Ang mahal ng diesel, apektado pati gulay galing Baguio dahil sa transport costs.", "2026-03-09", 43, "youtube", "https://youtube.com/watch?v=sample1", "Diesel is so expensive, even vegetables from Baguio are affected due to transport costs."),
    ("Inflation in basic necessities is killing small micro-businesses and karinderyas.", "2026-03-09", 98, "reddit", "https://reddit.com/r/Philippines/sample2", "Inflation in basic necessities is killing small micro-businesses and eateries."),
    ("Sobrang stress mag-budget tuwing kinsenas at katapusan. Wala nang natitira.", "2026-03-10", 72, "youtube", "https://youtube.com/watch?v=sample1", "Extremely stressful to budget every 15th and end of month. Nothing is left."),
    ("LPG cooking gas cylinder went up again. Almost 1000 pesos now per tank.", "2026-03-10", 50, "youtube", "https://youtube.com/watch?v=sample1", "LPG cooking gas cylinder went up again. Almost 1000 pesos now per tank."),
    ("Ang hirap mabuhay ngayon sa Pilipinas, lalo na kapag pamilyado ka at may mga bata.", "2026-03-11", 130, "youtube", "https://youtube.com/watch?v=sample1", "It's so hard to live in the Philippines today, especially when you have a family and kids."),
    ("Shrinkflation everywhere. Smaller bread portions, smaller canned goods, but higher prices.", "2026-03-11", 165, "reddit", "https://reddit.com/r/Philippines/sample2", "Shrinkflation everywhere. Smaller bread portions, smaller canned goods, but higher prices."),
    ("Bakit hindi mapababa ang presyo ng pagkain? Ang daming pangako pero wala namang nangyayari.", "2026-03-12", 84, "youtube", "https://youtube.com/watch?v=sample1", "Why can't food prices be lowered? So many promises but nothing happens."),
    ("Transportation fare hike will hurt everyday students and workers deeply.", "2026-03-12", 61, "reddit", "https://reddit.com/r/Philippines/sample2", "Transportation fare hike will hurt everyday students and workers deeply."),

    # Neutral comments (factual reporting, market statistics, analytical observations)
    ("The headline inflation rate for February clocked in at 3.4 percent according to PSA data.", "2026-03-01", 15, "reddit", "https://reddit.com/r/Philippines/sample2", "The headline inflation rate for February clocked in at 3.4 percent according to PSA data."),
    ("DA reports farmgate price of palay currently ranges from 21 to 23 pesos per kilo.", "2026-03-02", 20, "youtube", "https://youtube.com/watch?v=sample1", "DA reports farmgate price of palay currently ranges from 21 to 23 pesos per kilo."),
    ("BSP kept the policy interest rate steady at the latest monetary board meeting.", "2026-03-03", 28, "reddit", "https://reddit.com/r/Philippines/sample2", "BSP kept the policy interest rate steady at the latest monetary board meeting."),
    ("Global crude oil benchmarks traded sideways amid mixed supply forecasts.", "2026-03-04", 12, "youtube", "https://youtube.com/watch?v=sample1", "Global crude oil benchmarks traded sideways amid mixed supply forecasts."),
    ("A comparison of supermarket and wet market prices shows a 15 percent price differential.", "2026-03-05", 35, "reddit", "https://reddit.com/r/Philippines/sample2", "A comparison of supermarket and wet market prices shows a 15 percent price differential."),
    ("Consumer price index measures changes in the price level of a market basket of goods.", "2026-03-06", 9, "youtube", "https://youtube.com/watch?v=sample1", "Consumer price index measures changes in the price level of a market basket of goods."),
    ("Import tariffs on certain agricultural commodities are subject to review by NEDA.", "2026-03-07", 18, "reddit", "https://reddit.com/r/Philippines/sample2", "Import tariffs on certain agricultural commodities are subject to review by NEDA."),
    ("Core inflation excludes volatile items such as food and energy components.", "2026-03-08", 14, "reddit", "https://reddit.com/r/Philippines/sample2", "Core inflation excludes volatile items such as food and energy components."),
    ("Average diesel price in Metro Manila stands between 55 to 58 pesos per liter this week.", "2026-03-09", 22, "youtube", "https://youtube.com/watch?v=sample1", "Average diesel price in Metro Manila stands between 55 to 58 pesos per liter this week."),
    ("The National Wages and Productivity Commission reviews regional wage petitions periodically.", "2026-03-10", 17, "reddit", "https://reddit.com/r/Philippines/sample2", "The National Wages and Productivity Commission reviews regional wage petitions periodically."),
    ("Economists project inflation to hover near the central bank target band this quarter.", "2026-03-11", 31, "reddit", "https://reddit.com/r/Philippines/sample2", "Economists project inflation to hover near the central bank target band this quarter."),
    ("Philippine Statistics Authority will release the official price report next Tuesday morning.", "2026-03-12", 11, "youtube", "https://youtube.com/watch?v=sample1", "Philippine Statistics Authority will release the official price report next Tuesday morning."),

    # Positive comments (hopeful, praising assistance programs, solutions, optimism)
    ("Maganda ang programa ng Kadiwa store, mas mura ang bigas at sariwa ang gulay.", "2026-03-01", 105, "youtube", "https://youtube.com/watch?v=sample1", "The Kadiwa store program is good, rice is cheaper and vegetables are fresh."),
    ("Appreciate the targeted fuel subsidies helping jeepney drivers maintain their routes.", "2026-03-02", 74, "reddit", "https://reddit.com/r/Philippines/sample2", "Appreciate the targeted fuel subsidies helping jeepney drivers maintain their routes."),
    ("Buti na lang may solar panels kami sa bahay, malaking tulong sa pagbawas ng electricity bill.", "2026-03-03", 83, "youtube", "https://youtube.com/watch?v=sample1", "Good thing we have solar panels at home, a huge help in reducing electricity bill."),
    ("Local community gardens and urban farming are great initiatives that help families cope.", "2026-03-04", 62, "reddit", "https://reddit.com/r/Philippines/sample2", "Local community gardens and urban farming are great initiatives that help families cope."),
    ("Salamat sa mga kooperatiba na diretsong nagbebenta ng bigas galing sa magsasaka sa abot-kayang halaga.", "2026-03-05", 91, "youtube", "https://youtube.com/watch?v=sample1", "Thanks to cooperatives that sell rice directly from farmers at affordable prices."),
    ("Encouraging to see inflation numbers slowing down compared to last year's peak.", "2026-03-06", 58, "reddit", "https://reddit.com/r/Philippines/sample2", "Encouraging to see inflation numbers slowing down compared to last year's peak."),
    ("Malaking ginhawa ang libreng sakay sa mga piling ruta para sa mga manggagawa at estudyante.", "2026-03-07", 112, "youtube", "https://youtube.com/watch?v=sample1", "Free rides on selected routes provide big relief for workers and students."),
    ("Financial literacy and smart budgeting tips are truly empowering in these economic times.", "2026-03-08", 47, "reddit", "https://reddit.com/r/Philippines/sample2", "Financial literacy and smart budgeting tips are truly empowering in these economic times."),
    ("Good news that local harvests are improving supply and stabilizing prices of staple crops.", "2026-03-09", 69, "reddit", "https://reddit.com/r/Philippines/sample2", "Good news that local harvests are improving supply and stabilizing prices of staple crops."),
    ("Kahanga-hanga ang diskarte ng mga Pilipino, sama-sama at nagtutulungan para makaraos.", "2026-03-10", 134, "youtube", "https://youtube.com/watch?v=sample1", "Admirable how resourceful Filipinos are, united and helping each other overcome challenges."),
    ("Online discounts and group buying direct from local producers really save money.", "2026-03-11", 53, "reddit", "https://reddit.com/r/Philippines/sample2", "Online discounts and group buying direct from local producers really save money."),
    ("Hopeful that agricultural reforms and supply chain investments will bring long-term price relief.", "2026-03-12", 80, "reddit", "https://reddit.com/r/Philippines/sample2", "Hopeful that agricultural reforms and supply chain investments will bring long-term price relief.")
]


def seed(count_factor=3):
    """Seed data/raw/raw_comments.csv and data/processed/translations.json."""
    config.RAW.parent.mkdir(parents=True, exist_ok=True)
    config.CLEANED.parent.mkdir(parents=True, exist_ok=True)

    cache = json.loads(config.TRANSLATIONS.read_text()) if config.TRANSLATIONS.exists() else {}

    rows = []
    # duplicate with slight variations or timestamps to create enough samples for ML training
    for factor in range(count_factor):
        for text, date, reactions, platform, source, en in SEED_COMMENTS:
            sample_text = f"{text} (variant {factor})" if factor > 0 else text
            cache[sample_text] = f"{en} (variant {factor})" if factor > 0 else en
            rows.append({
                "text": sample_text,
                "timestamp": date,
                "reactions": reactions + factor * 2,
                "platform": platform,
                "source_post": source,
                "collected_at": "2026-11-23"
            })

    with open(config.RAW, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["text", "timestamp", "reactions", "platform", "source_post", "collected_at"])
        w.writeheader()
        w.writerows(rows)

    config.TRANSLATIONS.write_text(json.dumps(cache, indent=2, ensure_ascii=False))
    print(f"Seeded {len(rows)} comments into {config.RAW} and cached translations into {config.TRANSLATIONS}")


if __name__ == "__main__":
    seed()
