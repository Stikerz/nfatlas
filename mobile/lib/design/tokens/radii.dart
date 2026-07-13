/// Border-radius scale per `_bmad-output/planning-artifacts/design/tokens.md §4`.
/// Restraint over expressiveness. Nothing > 24px.
class AtlasRadius {
  const AtlasRadius._();

  static const double none = 0;
  static const double small = 4;   // inputs, tags
  static const double medium = 8;  // DEFAULT interactive (buttons, banners)
  static const double large = 12;  // cards, ticket cards, modals
  static const double pill = 9999; // ONLY skill-answer chips + free-entry pill
}
