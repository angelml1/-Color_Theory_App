# reusable info on what color theory is, why it's used, etc.

THEORY_INFO = {
    # info on surround tab
    # parts referenced from url: https://www.exploratorium.edu/snacks/color-contrast
    "surround": {
        "title": "Surround Effects (Color Contrast)",
        "text": "    Colors are always in context, and are often influenced by the colors around "
                "them. A color with a mid-range value (brightness) looks darker on a light "
                "background and ligher on a dark background. Hue can also shift, such as a "
                "neutral grey appearing cooler on red or orange backgrounds, or warmer on blue or "
                "green backgrounds.\n    This happens because when the cone cells in your eye are "
                "exposed to large swathes of a particular color, nearby cones become less "
                "sensitive to that color, making any changes in hue deviate further from that "
                "color. Similar effects can be seen in such illusions as the afterimage effect, "
                "where one looks at an inverted-color image for a period of time, then looks at a "
                "white surface, where a ghostly correct-color version of the image can be "
                "percieved.",
        },
    "match": {
        "title": "Matching Colors Across Backgrounds",
        "text": "    Color contrast, mentioned in the previous \"Surround\" section, also works "
                "in the opposite direction: against the right backgrounds, two different colors "
                "can perceptually appear the same. This is done by \"cancelling\" out the "
                "perceived shifts in value or hue, like lightening a color that appears dark on "
                "a light background on a more neutral background.",
        },
    # info on glow tab
    # some info from url: 
    # https://www.physicsclassroom.com/tutorial/light-waves-and-colors/physics-of-color/light-absorption-reflection-and-transmission
    "glow": {
        "title": "Glow",
        "text": "    In \"Light on Surface\" mode, the glow is treated as real light landing on "
                "the surface, so a red glow barely shows up on a green surface, but lights up a "
                "white or warm one.\n    \"Bloom\" is a different idea: a soft halo added on top "
                "of the image no matter what's underneath, inspired by how bright lights look "
                "through an imperfect lens. It's not physically accurate, and very bright blooms "
                "wash out toward white, as they do here. In both modes the glow fades with "
                "distance, loosely like real light does, but the curve is simplified, chosen to "
                "look smooth. Lower the ambient light to make the glow stand out, since less "
                "other light competes with it.",
        },
    # info on light & shadow tab
    # some info from url: 
    # https://www.carolynanderson.com/blog/147747/warmer-light-does-have-cooler-shadows-heres-why
    "shadow": {
        "title": "Colored Light and Shadows",
        "text": "    Shadows aren't only a darker version of a surface, but is influenced by "
                "whatever light can still reach it, like skylight or light bouncing off of"
                "nearby objects, and that light often has a different color than the "
                "main light. Painters use this a lot: under warm sunlight, shadows tend "
                "to be cooler, and the reverse.\n    Here, light color and brightness "
                "control everything in the sunny areas, and shadow tint and darkness "
                "control everything in the shadows, so the two sets never affect each "
                "other.",
        },
    "relight": {
        "title": "Relighting Your Palette",
        "text": "See how every color in your palette changes under one light, and in the "
                "shadow where only the fill light reaches. Colors that are far from the "
                "light's hue lose the most. Click any result to add it to your palette.",
    },
    "model": {
        "title": "How the lighting works",
        "text": "    Light adds together and surfaces multiply. A surface's color is the "
                "share of red, green, and blue light it reflects, so the color you see is "
                "the surface color times the light that lands on it. The sandbox does "
                "this in linear light, not raw sRGB values, which matches how real light "
                "behaves. It's an RGB approximation: real pigments reflect a full "
                "spectrum, so mixed paint can behave differently than shown here.",
        },
}
