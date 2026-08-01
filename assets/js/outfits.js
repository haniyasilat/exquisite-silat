const OUTFITS = [
  {
    id: "teal-elevate-look-01",
    title: "Elevate the Basics with Teal",
    description:
      "Start with a white ribbed top and white maxi skirt, then layer in teal — satin shirt, turquoise tote, gold jewellery, braided belt, and brown kitten heels for Summer 2026.",
    categories: ["Casual", "Summer"],
    collage_image: "assets/products/teal-elevate-look/collage.png?v=2",
    pieces: [
      { slot: "Top", label: "White Ribbed Boat-Neck Top", amazon_url: "https://link.amazon/B0jlViWJq" },
      { slot: "Skirt", label: "White Boho Elastic Waist Maxi Skirt", amazon_url: "https://link.amazon/B0h2sv9CT" },
      { slot: "Shirt", label: "Teal Satin Button-Down Shirt", amazon_url: "https://link.amazon/B07tPuDs1" },
      { slot: "Bag", label: "Turquoise Shoulder Tote Bag", amazon_url: "https://link.amazon/B0j4P8T2Q" },
      { slot: "Belt", label: "Brown Braided Leather Belt", amazon_url: "https://link.amazon/B0gvpdUeN" },
      { slot: "Earrings", label: "Chunky Gold Knot Earrings", amazon_url: "https://link.amazon/B0b8nLrrj" },
      { slot: "Jewelry", label: "Gold Statement Ring Set", amazon_url: "https://link.amazon/B0ejFsCDh" },
      { slot: "Heels", label: "Brown Strappy Kitten Heel Sandals", amazon_url: "https://link.amazon/B0dW22S1Q" },
    ],
  },
  {
    id: "navy-gingham-look-01",
    title: "Navy Stripe & Gingham Casual",
    description:
      "Navy and cream striped knit sweater, white wide-leg jeans, light blue crescent shoulder bag, turquoise dial silver watch, navy polka-dot phone case, and white New Balance sneakers.",
    categories: ["Casual", "Summer"],
    collage_image: "assets/products/navy-gingham-look/collage.png",
    pieces: [
      { slot: "Sweater", label: "Navy & Cream Striped Knit Sweater", amazon_url: "https://link.amazon/B03PPwYwt" },
      { slot: "Jeans", label: "High-Rise White Wide-Leg Jeans", amazon_url: "https://link.amazon/B01Fu3dFj" },
      { slot: "Bag", label: "Light Blue Crescent Shoulder Bag", amazon_url: "https://link.amazon/B04DsHUts" },
      { slot: "Watch", label: "Silver Link Watch with Turquoise Dial", amazon_url: "https://link.amazon/B02Wszqib" },
      { slot: "Phone Case", label: "Navy Polka-Dot Phone Case", amazon_url: "https://link.amazon/B0gt0tzFN" },
      { slot: "Shoes", label: "White & Navy New Balance Sneakers", amazon_url: "https://link.amazon/B0czdKvRi" },
    ],
  },
  {
    id: "blush-pearl-look-01",
    title: "Blush Pink & Pearl Elegance",
    description:
      "Dusty rose cropped cardigan, white ribbed boat-neck top, white tiered maxi skirt, pearl swirl stud earrings, iridescent pearl clutch, Delina perfume, and silver block-heel sandals.",
    categories: ["Fancy", "Spring", "Summer"],
    collage_image: "assets/products/blush-pearl-look/collage.png",
    pieces: [
      { slot: "Cardigan", label: "Dusty Rose Cropped Knit Cardigan", amazon_url: "https://link.amazon/B0eTIlIZ3" },
      { slot: "Top", label: "White Ribbed Boat-Neck Top", amazon_url: "https://link.amazon/B05dzB2tX" },
      { slot: "Skirt", label: "White Tiered Maxi Skirt", amazon_url: "https://link.amazon/B05vXeHy2" },
      { slot: "Earrings", label: "Pearl & Gold Swirl Stud Earrings", amazon_url: "https://link.amazon/B05pJbaR5" },
      { slot: "Bag", label: "Iridescent Pearl Clutch", amazon_url: "https://link.amazon/B01b5DU1u" },
      { slot: "Perfume", label: "Parfums de Marly Delina", amazon_url: "https://link.amazon/B0cQRsonl" },
      { slot: "Shoes", label: "Silver Block-Heel Sandals", amazon_url: "https://link.amazon/B0ivktgsn" },
    ],
  },
  {
    id: "navy-cream-lace-look-01",
    title: "Cream Lace & Denim Elegance",
    description:
      "Cream satin lace-trim blouse, light-wash wide-leg jeans, cream lace slingback heels, gold Casio watch, monogram crescent bag, sculptural gold earrings, and two gold rings.",
    categories: ["Fancy", "Casual"],
    collage_image: "assets/products/navy-cream-lace-look/collage.png?v=3",
    pieces: [
      { slot: "Shirt", label: "Ivory Satin Blouse with Lace Trim", amazon_url: "https://link.amazon/B06TdBEC9" },
      { slot: "Jeans", label: "High-Rise Wide-Leg Denim Jeans", amazon_url: "https://link.amazon/B0flegnpy" },
      { slot: "Heels", label: "Ivory Lace Slingback Kitten Heels", amazon_url: "https://link.amazon/B0ftkt2K0" },
      { slot: "Watch", label: "Gold Square Dial Classic Watch", amazon_url: "https://link.amazon/B06zbNtAC" },
      { slot: "Bag", label: "Monogram Crescent Shoulder Bag", amazon_url: "https://link.amazon/B09bdGyS0" },
      { slot: "Earrings", label: "Polished Gold Statement Earrings", amazon_url: "https://link.amazon/B04c6iMF4" },
      { slot: "Ring", label: "Gold Swirl Knot Ring", amazon_url: "https://link.amazon/B0c0r4ks1" },
      { slot: "Ring", label: "Wide Ridged Gold Band Ring", amazon_url: "https://link.amazon/B0diMh7cS" },
    ],
  },
  {
    id: "brown-leather-look-01",
    title: "Brown Leather & Denim Chic",
    description:
      "Dark brown faux-leather bomber jacket, white ribbed boat-neck top, dark wide-leg jeans, brown leather belt, gold teardrop earrings, structured brown handbag, and square-toe ankle boots.",
    categories: ["Casual", "Autumn"],
    collage_image: "assets/products/brown-leather-look/collage.png?v=3",
    pieces: [
      { slot: "Earrings", label: "Gold Teardrop Earrings", amazon_url: "https://link.amazon/B06pH01dF" },
      { slot: "Belt", label: "Brown Leather Belt", amazon_url: "https://link.amazon/B0gD3bPRB" },
      { slot: "Jeans", label: "Dark Wide-Leg Jeans", amazon_url: "https://link.amazon/B0ia1Qpfq" },
      { slot: "Top", label: "White Ribbed Boat-Neck Top", amazon_url: "https://link.amazon/B07zv37VP" },
      { slot: "Jacket", label: "Dark Brown Faux-Leather Bomber Jacket", amazon_url: "https://link.amazon/B07hqp4v9" },
      { slot: "Shoes", label: "Square-Toe Ankle Boots", amazon_url: "https://link.amazon/B03VLdF5a" },
      { slot: "Bag", label: "Structured Brown Handbag", amazon_url: "https://link.amazon/B0jlQuyKO" },
    ],
  },
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
