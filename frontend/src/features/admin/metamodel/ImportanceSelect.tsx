import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import { useTranslation } from "react-i18next";

/**
 * Labeled data-quality importance picker. Maps the underlying numeric `weight`
 * (0 = excluded, higher = counts more) to four intuitive levels:
 *   Ignore = 0, Normal = 1, Important = 2, Critical = 3.
 *
 * Legacy/out-of-range weights are snapped to the nearest level for display but
 * never silently rewritten until the admin actively changes the selection.
 */

export const IMPORTANCE_LEVELS = [0, 1, 2, 3] as const;

export function weightToLevel(weight: number | undefined): number {
  const w = weight ?? 1;
  if (w <= 0) return 0;
  if (w < 2) return 1;
  if (w < 3) return 2;
  return 3;
}

interface ImportanceSelectProps {
  value: number | undefined;
  onChange: (weight: number) => void;
  label?: string;
  size?: "small" | "medium";
  fullWidth?: boolean;
  sx?: object;
}

export default function ImportanceSelect({
  value,
  onChange,
  label,
  size = "small",
  fullWidth,
  sx,
}: ImportanceSelectProps) {
  const { t } = useTranslation("admin");
  const labelText = label ?? t("metamodel.importance.label");
  const level = weightToLevel(value);

  const levelLabels: Record<number, string> = {
    0: t("metamodel.importance.ignore"),
    1: t("metamodel.importance.normal"),
    2: t("metamodel.importance.important"),
    3: t("metamodel.importance.critical"),
  };

  return (
    <FormControl size={size} fullWidth={fullWidth} sx={{ minWidth: 160, ...sx }}>
      <InputLabel>{labelText}</InputLabel>
      <Select
        label={labelText}
        value={level}
        onChange={(e) => onChange(Number(e.target.value))}
      >
        {IMPORTANCE_LEVELS.map((lvl) => (
          <MenuItem key={lvl} value={lvl}>
            {levelLabels[lvl]}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
}
