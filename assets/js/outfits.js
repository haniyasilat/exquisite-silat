const OUTFITS = [
  {
    id: "plaid-autumn-look-01",
    title: "Plaid & Burgundy Autumn",
    description:
      "Burgundy ruched top, plaid belted maxi skirt, cream chunky cardigan, gold heart locket necklace, hoop earrings, retro sunglasses, black shoulder bag, and burgundy Converse high-tops.",
    categories: ["Casual", "Autumn", "Modest"],
    collage_image: "assets/products/plaid-autumn-look/collage.png",
    pieces: [
      { slot: "Top", label: "CIDER Burgundy Boat Neck Ruched Top", amazon_url: "https://link.amazon/B0bQwE0Wp" },
      { slot: "Skirt", label: "GORGLITTER Plaid Belted Maxi Skirt", amazon_url: "https://link.amazon/B0bk2glQ1" },
      { slot: "Cardigan", label: "Arssm Chunky Cropped Cardigan", amazon_url: "https://link.amazon/B01ejqyHj" },
      { slot: "Necklace", label: "Heart Sunflower Locket Necklace", amazon_url: "https://link.amazon/B01I95woS" },
      { slot: "Earrings", label: "Gold Chunky Hoop Earrings", amazon_url: "https://link.amazon/B0h2yihG9" },
      { slot: "Sunglasses", label: "KENBO Retro Y2K Sunglasses", amazon_url: "https://link.amazon/B03xq88cj" },
      { slot: "Bag", label: "Black PU Leather Shoulder Bag", amazon_url: "https://link.amazon/B036SFQ5I" },
      { slot: "Shoes", label: "Converse Chuck Taylor Hi Red", amazon_url: "https://link.amazon/B05eIJuvq" },
    ],
  },
  {
    id: "polka-dot-look-01",
    title: "Polka Dot & Black Chic",
    description:
      "White polka-dot bell sleeve top, black wide-leg trousers, patent pumps, marble pearl clutch, and twisted pearl earrings.",
    categories: ["Fancy", "Casual"],
    collage_image: "assets/products/polka-dot-look/collage.png",
    pieces: [
      {
        slot: "Top",
        label: "Cicy Bell Polka Dot Bell Sleeve Top",
        amazon_url: "https://link.amazon/B09AW8fJE",
      },
      {
        slot: "Bottom",
        label: "NIMIN Black Wide-Leg Trousers",
        amazon_url: "https://link.amazon/B0jdFdrDa",
      },
      {
        slot: "Shoes",
        label: "Calvin Klein Gloria Patent Pump",
        amazon_url: "https://link.amazon/B0gfFXWdx",
      },
      {
        slot: "Bag",
        label: "Marble Pearl Acrylic Clutch",
        amazon_url: "https://link.amazon/B07D0E0Qs",
      },
      {
        slot: "Earrings",
        label: "Gold Twisted Pearl Drop Earrings",
        amazon_url: "https://link.amazon/B02T3U6iL",
      },
    ],
  },
  {
    id: "red-floral-coquette-01",
    title: "Denim & Cherry Coquette",
    description:
      "Darker denim bow blouse, white tiered maxi skirt, cherry red Mary Janes and bow bag, gold earrings, and Daisy perfume.",
    categories: ["Fancy", "Summer"],
    collage_image: "assets/products/red-floral-look/collage.png",
    pieces: [
      { slot: "Top", label: "Denim Tie-Front Babydoll Blouse", amazon_url: "https://link.amazon/B0ahpzR7z" },
      { slot: "Skirt", label: "GORGLITTER White Tiered Maxi Skirt", amazon_url: "https://link.amazon/B0dF0T4jL" },
      { slot: "Shoes", label: "TN TANGNEST Red Mary Jane Flats", amazon_url: "https://link.amazon/B0fO82l8Z" },
      { slot: "Bag", label: "Amszke Cherry Red Bow Bag", amazon_url: "https://link.amazon/B03SLr3nF" },
      { slot: "Earrings", label: "Gold Teardrop Earrings", amazon_url: "https://link.amazon/B0bWLrfPy" },
      { slot: "Perfume", label: "Marc Jacobs Daisy", amazon_url: "https://link.amazon/B07xS1km3" },
    ],
  },
  {
    id: "blue-yellow-summer-look-01",
    title: "Yellow & Navy Summer Coastal",
    description:
      "Butter-yellow wrap blouse, navy wide-leg jeans, tortoise sandals and sunnies, brown tote, and seashell gold jewelry.",
    categories: ["Casual", "Summer"],
    collage_image: "assets/products/blue-yellow-look/collage.png",
    pieces: [
      {
        slot: "Top",
        label: "GORGLITTER Yellow Asymmetrical Blouse",
        amazon_url: "https://link.amazon/B0d72SrXR",
      },
      {
        slot: "Bottom",
        label: "Glossia Navy High-Rise Wide Jeans",
        amazon_url: "https://link.amazon/B00JGpsVj",
      },
      {
        slot: "Shoes",
        label: "Steve Madden Hadyn Tortoise Sandals",
        amazon_url: "https://link.amazon/B00jfHP4y",
      },
      {
        slot: "Bag",
        label: "JW PEI Hana Dark Brown Tote",
        amazon_url: "https://link.amazon/B03vk2Ulu",
      },
      {
        slot: "Glasses",
        label: "SOJOS Tortoise Polarized Sunglasses",
        amazon_url: "https://link.amazon/B0i13rp9X",
      },
      {
        slot: "Necklace",
        label: "Gold Seashell & Starfish Necklace",
        amazon_url: "https://link.amazon/B0flGicUX",
      },
      {
        slot: "Earrings",
        label: "Gold Seashell Jewelry Set",
        amazon_url: "https://link.amazon/B0flGicUX",
      },
    ],
  },
  {
    id: "burgundy-casual-look-01",
    title: "Burgundy & Black Casual",
    description:
      "A polished everyday look — asymmetrical burgundy top, wide-leg black jeans, croc bag, and burgundy slingbacks with gold accents.",
    categories: ["Casual", "Autumn"],
    collage_image: "assets/products/burgundy-look/collage.png",
    pieces: [
      {
        slot: "Top",
        label: "PRETTYGARDEN Burgundy Asymmetrical Top",
        amazon_url: "https://link.amazon/B08TSRX9K",
      },
      {
        slot: "Bottom",
        label: "KOTTY Black High-Rise Wide Jeans",
        amazon_url: "https://link.amazon/B0hdpJOr3",
      },
      {
        slot: "Shoes",
        label: "Mattiventon Burgundy Bow Slingbacks",
        amazon_url: "https://link.amazon/B0drwncy3",
      },
      {
        slot: "Bag",
        label: "JW PEI Harlee Brown Croc Bag",
        amazon_url: "https://link.amazon/B0cvbClLk",
      },
      {
        slot: "Watch",
        label: "FANMIS Brown & Gold Rectangle Watch",
        amazon_url: "https://link.amazon/B0cYvoLpG",
      },
      {
        slot: "Jewelry",
        label: "Gold Teardrop Hoop Earrings",
        amazon_url: "https://link.amazon/B0104bp0b",
      },
    ],
  },
  {
    id: "sample-summer-casual-01",
    title: "Easy Summer Casual",
    description: "Add a short outfit description here.",
    categories: ["Casual", "Summer"],
    pieces: [
      { slot: "Top", label: "Add item name" },
      { slot: "Bottom", label: "Add item name" },
      { slot: "Shoes", label: "Add item name" },
      { slot: "Bag", label: "Add item name" },
      { slot: "Jewelry", label: "Add item name" },
      { slot: "Belt", label: "Add item name" },
    ],
  },
  {
    id: "sample-fancy-dress-01",
    title: "Evening Dress Look",
    description: "Add a short outfit description here.",
    categories: ["Fancy", "Autumn"],
    pieces: [
      { slot: "Dress", label: "Add item name" },
      { slot: "Shoes", label: "Add item name" },
      { slot: "Bag", label: "Add item name" },
      { slot: "Jewelry", label: "Add item name" },
    ],
  },
  {
    id: "sample-modest-spring-01",
    title: "Modest Spring Layers",
    description: "Add a short outfit description here.",
    categories: ["Modest", "Spring"],
    pieces: [
      { slot: "Top", label: "Add item name" },
      { slot: "Bottom", label: "Add item name" },
      { slot: "Shoes", label: "Add item name" },
      { slot: "Bag", label: "Add item name" },
      { slot: "Jewelry", label: "Add item name" },
      { slot: "Belt", label: "Add item name" },
    ],
  },
  {
    id: "sample-winter-cozy-01",
    title: "Winter Cozy Layers",
    description: "Add a short outfit description here.",
    categories: ["Casual", "Winter"],
    pieces: [
      { slot: "Top", label: "Add item name" },
      { slot: "Bottom", label: "Add item name" },
      { slot: "Shoes", label: "Add item name" },
      { slot: "Bag", label: "Add item name" },
      { slot: "Jewelry", label: "Add item name" },
      { slot: "Belt", label: "Add item name" },
    ],
  },
  {
    id: "sample-summer-fancy-01",
    title: "Sunny Fancy Brunch",
    description: "Add a short outfit description here.",
    categories: ["Fancy", "Summer"],
    pieces: [
      { slot: "Dress", label: "Add item name" },
      { slot: "Shoes", label: "Add item name" },
      { slot: "Bag", label: "Add item name" },
      { slot: "Jewelry", label: "Add item name" },
    ],
  },
  {
    id: "sample-modest-autumn-01",
    title: "Modest Autumn Neutrals",
    description: "Add a short outfit description here.",
    categories: ["Modest", "Autumn"],
    pieces: [
      { slot: "Top", label: "Add item name" },
      { slot: "Bottom", label: "Add item name" },
      { slot: "Shoes", label: "Add item name" },
      { slot: "Bag", label: "Add item name" },
      { slot: "Jewelry", label: "Add item name" },
      { slot: "Belt", label: "Add item name" },
    ],
  },
];

function collageFrameInner(o) {
  if (o.collage_image) {
    return `<img src="${o.collage_image}" alt="${o.title} outfit collage" loading="lazy" />`;
  }
  return `
        <div>
          <strong>Add your collage here</strong>
          Top · Bottom · Accessories · Shoes
        </div>`;
}

function outfitCardHTML(o) {
  const hasImage = Boolean(o.collage_image);
  return `
    <a class="outfit-card" href="look.html?id=${encodeURIComponent(o.id)}">
      <div class="collage-frame${hasImage ? " collage-frame--has-image" : ""}">
        ${collageFrameInner(o)}
      </div>
      <h3 class="outfit-card__title">${o.title}</h3>
      <p class="outfit-card__desc">${o.description}</p>
    </a>
  `;
}

function getOutfitById(id) {
  return OUTFITS.find((o) => o.id === id);
}

function outfitsForCategory(cat) {
  return OUTFITS.filter((o) =>
    o.categories.some((c) => c.toLowerCase() === String(cat).toLowerCase())
  );
}
