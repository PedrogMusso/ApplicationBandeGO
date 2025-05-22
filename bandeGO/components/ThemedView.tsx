import { View, type ViewProps } from "react-native";

export type ThemedViewProps = ViewProps & {
  lightColor?: string;
  darkColor?: string;
  styleProps?: string;
};

export function ThemedView({
  lightColor,
  darkColor,
  styleProps,
  ...otherProps
}: ThemedViewProps) {
  return <View className={styleProps} {...otherProps} />;
}
