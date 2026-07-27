const OUTFITS = [
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

function outfitCardHTML(o) {
  return `
    <a class="outfit-card" href="look.html?id=${encodeURIComponent(o.id)}">
      <div class="collage-frame">
        <div>
          <strong>Add your collage here</strong>
          Top · Bottom · Accessories · Shoes
        </div>
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
