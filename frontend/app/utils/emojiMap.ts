const itemEmojis: Record<string, string> = {
  milk: '\u{1F95B}',
  banana: '\u{1F34C}',
  apple: '\u{1F34E}',
  chicken: '\u{1F357}',
  bread: '\u{1F35E}',
  coffee: '\u2615',
  pasta: '\u{1F35D}',
  rice: '\u{1F35A}',
  egg: '\u{1F95A}',
  cheese: '\u{1F9C0}',
  butter: '\u{1F9C8}',
  yogurt: '\u{1F95B}',
  tomato: '\u{1F345}',
  potato: '\u{1F954}',
  onion: '\u{1F9C5}',
  carrot: '\u{1F955}',
  lettuce: '\u{1F96C}',
  pepper: '\u{1FAD1}',
  broccoli: '\u{1F966}',
  corn: '\u{1F33D}',
  fish: '\u{1F41F}',
  salmon: '\u{1F41F}',
  beef: '\u{1F969}',
  pork: '\u{1F969}',
  steak: '\u{1F969}',
  shrimp: '\u{1F990}',
  orange: '\u{1F34A}',
  lemon: '\u{1F34B}',
  strawberry: '\u{1F353}',
  blueberry: '\u{1FAD0}',
  grape: '\u{1F347}',
  watermelon: '\u{1F349}',
  avocado: '\u{1F951}',
  mushroom: '\u{1F344}',
  garlic: '\u{1F9C4}',
  sugar: '\u{1F36C}',
  oil: '\u{1FAD2}',
  juice: '\u{1F9C3}',
  water: '\u{1F4A7}',
  cereal: '\u{1F963}',
  soup: '\u{1F372}',
  pizza: '\u{1F355}',
  sausage: '\u{1F32D}',
  bacon: '\u{1F953}',
  ham: '\u{1F356}',
  cream: '\u{1F95B}',
};

const categoryEmojis: Record<string, string> = {
  dairy: '\u{1F95B}',
  produce: '\u{1F96C}',
  meat: '\u{1F969}',
  bakery: '\u{1F35E}',
  beverages: '\u{1F964}',
  pantry: '\u{1F96B}',
  frozen: '\u{1F9CA}',
  snacks: '\u{1F36A}',
  seafood: '\u{1F41F}',
  deli: '\u{1F956}',
  condiments: '\u{1F9C2}',
};

export function getItemEmoji(itemName: string, categoryName?: string | null): string {
  const lower = itemName.toLowerCase();
  for (const [key, emoji] of Object.entries(itemEmojis)) {
    if (lower.includes(key)) return emoji;
  }
  if (categoryName) {
    const catLower = categoryName.toLowerCase();
    for (const [key, emoji] of Object.entries(categoryEmojis)) {
      if (catLower.includes(key)) return emoji;
    }
  }
  return '\u{1F6D2}';
}

export function getCategoryEmoji(categoryName: string): string {
  const catLower = categoryName.toLowerCase();
  for (const [key, emoji] of Object.entries(categoryEmojis)) {
    if (catLower.includes(key)) return emoji;
  }
  return '\u{1F6D2}';
}
