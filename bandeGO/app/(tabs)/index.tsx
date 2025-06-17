import React, { useState, useCallback, useEffect, useTransition } from "react";
import { View, Text } from "react-native";
import ParallaxScrollView from "@/components/ParallaxScrollView";
import { ThemedText } from "@/components/ThemedText";
import { ThemedView } from "@/components/ThemedView";
import { FoodCard } from "@/components/FoodCard";
import { LocationSelector } from "@/components/ui/locationSelect";
import {
  MealItem,
  DayOfWeek,
  restaurantData,
} from "@/components/MockLists/MockMeals";
import { Button, ButtonText, ButtonSpinner } from "@/components/ui/button";
import { api } from "@/services/api";
import { Icon, RepeatIcon } from "@/components/ui/icon";

export default function HomeScreen() {
  const [selectedLocationId, setSelectedLocationId] = useState<string | null>(
    null
  );
  const [selectedDay, setSelectedDay] = useState<DayOfWeek | null>(null);
  const [count, setCount] = useState<number | null>(0);
  const [isPending, startTransition] = useTransition();

  const formatTime = (totalSeconds: number | null) => {
    // Se o tempo for 0 ou inválido, exibe "0 segundos"
    if (!totalSeconds || totalSeconds <= 0) {
      return "0 segundos";
    }

    // Calcula os minutos e segundos
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;

    // Monta as partes do texto
    const minutesText =
      minutes > 0 ? `${minutes} minuto${minutes > 1 ? "s" : ""}` : "";
    const secondsText =
      seconds > 0 ? `${seconds} segundo${seconds > 1 ? "s" : ""}` : "";

    // Junta as partes com "e" se ambas existirem
    if (minutesText && secondsText) {
      return `${minutesText} e ${secondsText}`;
    }

    // Retorna apenas a parte que existe
    return minutesText || secondsText;
  };

  const handleLocationAndDaySelection = useCallback(
    (locationId: string | null, day: DayOfWeek | null) => {
      setSelectedLocationId(locationId);
      setSelectedDay(day);
    },
    []
  );

  const currentMenu: MealItem[] = React.useMemo(() => {
    if (!selectedLocationId || !selectedDay) {
      return [];
    }

    const location = restaurantData.find(
      (loc) => loc.id === selectedLocationId
    );
    if (!location) {
      return [];
    }

    const dailyMenu = location.dailyMenus.find(
      (dm) => dm.dayOfWeek === selectedDay
    );
    return dailyMenu ? dailyMenu.menuItems : [];
  }, [selectedLocationId, selectedDay]);

  const handleLocationConfirmed = useCallback(async () => {
    if (!selectedLocationId) return;

    try {
      const response = await api.get("/getCount");
      console.log("Contagem recebida:", response.data);
      const totalSeconds = response.data.count * 15;
      startTransition(() => {
        setCount(totalSeconds);
      });
    } catch (error) {
      console.error("Erro ao buscar contagem:", error);
      startTransition(() => {
        setCount(0);
      });
    }
  }, [selectedLocationId]);

  useEffect(() => {
    if (selectedLocationId && selectedDay) {
      handleLocationConfirmed();
    }
  }, [selectedLocationId, selectedDay, handleLocationConfirmed]);

  return (
    <ParallaxScrollView
      headerBackgroundColor={{ light: "#A1CEDC", dark: "#1D3D47" }}
    >
      <ThemedView styleProps="flex w-full flex-col items-center py-8">
        <ThemedText type="title">Bem-vindo!</ThemedText>
        {selectedLocationId ? (
          <ThemedView styleProps="flex flex-row items-center justify-between w-full">
            <Button className="mt-4 h-16 flex text-center justify-center items-center w-[80%] bg-[#FF8A37]">
              {isPending ? (
                <ButtonSpinner />
              ) : (
                <ButtonText
                  style={{
                    height: 56,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 16,
                  }}
                >
                  {selectedLocationId
                    ? `Tempo para ser atendido: ${formatTime(count)}`
                    : ""}
                </ButtonText>
              )}
            </Button>
            <Button
              onPress={handleLocationConfirmed}
              isDisabled={isPending}
              className="mt-4 bg-[#FF8A37] h-16"
            >
              <Icon as={RepeatIcon} />
            </Button>
          </ThemedView>
        ) : (
          <></>
        )}
      </ThemedView>

      <ThemedView styleProps="flex flex-col w-full items-center justify-center p-4">
        <ThemedText className="text-xl font-bold mb-4">
          Opção de Bandeijão
        </ThemedText>
        <LocationSelector onSelection={handleLocationAndDaySelection} />

        {selectedLocationId && selectedDay && currentMenu.length > 0 ? (
          <ThemedView styleProps="flex flex-col w-full justify-center items-center">
            <ThemedText className="text-lg font-semibold mb-4">
              Menu de{" "}
              {restaurantData.find((l) => l.id === selectedLocationId)?.name}{" "}
              para {selectedDay}
            </ThemedText>
            {currentMenu.map((meal, index) => (
              <FoodCard
                key={`${selectedLocationId}-${selectedDay}-${index}`}
                title={meal.title}
                description={meal.description}
                notes={meal.notes}
                image={meal.image}
              />
            ))}
          </ThemedView>
        ) : (
          <View className="mt-8 p-4 bg-gray-100 rounded-lg">
            <Text className="text-gray-600 text-center">
              Selecione um local e um dia da semana para ver o menu.
            </Text>
          </View>
        )}
      </ThemedView>
    </ParallaxScrollView>
  );
}
