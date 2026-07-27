const OUTFITS = [
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
