import { describe, it, expect } from "vitest";
import { weightToLevel } from "./ImportanceSelect";

describe("weightToLevel", () => {
  it("maps undefined to Normal (1) so unset weights count by default", () => {
    expect(weightToLevel(undefined)).toBe(1);
  });

  it("maps 0 to Ignore", () => {
    expect(weightToLevel(0)).toBe(0);
  });

  it("maps negative weights to Ignore", () => {
    expect(weightToLevel(-3)).toBe(0);
  });

  it("maps the canonical weights to their levels", () => {
    expect(weightToLevel(1)).toBe(1); // Normal
    expect(weightToLevel(2)).toBe(2); // Important
    expect(weightToLevel(3)).toBe(3); // Critical
  });

  it("snaps legacy out-of-range weights to the nearest level without rewriting", () => {
    expect(weightToLevel(1.5)).toBe(1);
    expect(weightToLevel(5)).toBe(3); // legacy high weight → Critical
  });
});
