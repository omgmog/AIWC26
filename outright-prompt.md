The 2026 FIFA World Cup begins today, 11 June 2026. Before the opening
match kicks off, give your outright tournament predictions.

The 48 qualified teams are: Algeria, Argentina, Australia, Austria,
Belgium, Bosnia & Herzegovina, Brazil, Canada, Cape Verde, Colombia,
Croatia, Curaçao, Czechia, DR Congo, Ecuador, Egypt, England, France,
Germany, Ghana, Haiti, Iran, Iraq, Ivory Coast, Japan, Jordan, Mexico,
Morocco, Netherlands, New Zealand, Norway, Panama, Paraguay, Portugal,
Qatar, Saudi Arabia, Scotland, Senegal, South Africa, South Korea,
Spain, Sweden, Switzerland, Tunisia, Türkiye, United States, Uruguay,
Uzbekistan.

Return ONLY a single JSON object, no markdown fences, no commentary,
matching this schema exactly:

{
  "model": "<your model name and version>",
  "generated": "2026-06-11",
  "champion": "<team>",
  "finalists": ["<team>", "<team>"],
  "semi_finalists": ["<team>", "<team>", "<team>", "<team>"],
  "reasoning": "<one or two sentences on your champion pick>"
}

Rules:
- Use team names exactly as written in the list above
- The champion must be one of the two finalists
- Both finalists must be among the four semi-finalists
- All four semi-finalists must be distinct qualified teams