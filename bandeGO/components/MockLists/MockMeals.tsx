export type DayOfWeek =
  | "Segunda-feira"
  | "Terça-feira"
  | "Quarta-feira"
  | "Quinta-feira"
  | "Sexta-feira"
  | "Sábado"
  | "Domingo";

export interface MealItem {
  image?: string;
  title: string;
  description: string;
  notes?: string;
}

export interface DailyMenu {
  dayOfWeek: DayOfWeek;
  menuItems: MealItem[];
}

export interface Location {
  id: string;
  name: string;
  address: string;
  cuisine?: string;
  dailyMenus: DailyMenu[];
}

export const restaurantData: Location[] = [
  {
    id: "restaurante-sabor-caseiro",
    name: "Restaurante Sabor Caseiro",
    address: "Rua das Flores, 123 - Centro",
    cuisine: "Comida Caseira",
    dailyMenus: [
      {
        dayOfWeek: "Segunda-feira",
        menuItems: [
          {
            title: "Entrada",
            description: "Salada de chicória, pepino e molho de limão",
            image: "https://via.placeholder.com/150/FF5733/FFFFFF?text=Salada",
          },
          {
            title: "Prato Principal",
            description: "Mignon suíno ao lemon pepper",
            notes: "(temos opção sem molho, contém pimenta do reino e cúrcuma)",
            image: "https://via.placeholder.com/150/C70039/FFFFFF?text=Mignon",
          },
          {
            title: "Acompanhamentos",
            description: "Arroz branco ou integral e feijão preto",
            image: "https://via.placeholder.com/150/900C3F/FFFFFF?text=Arroz",
          },
          {
            title: "Sobremesa",
            description: "Pera",
            image: "https://via.placeholder.com/150/581845/FFFFFF?text=Pera",
          },
        ],
      },
      {
        dayOfWeek: "Terça-feira",
        menuItems: [
          {
            title: "Entrada",
            description: "Sopa de legumes da estação",
            image: "https://via.placeholder.com/150/FFC300/000000?text=Sopa",
          },
          {
            title: "Prato Principal",
            description: "Frango grelhado com purê de batatas",
            image: "https://via.placeholder.com/150/DAF7A6/000000?text=Frango",
          },
          {
            title: "Prato Vegano",
            description: "Escondidinho de abóbora com carne de jaca",
            image: "https://via.placeholder.com/150/FFC300/000000?text=Vegano",
          },
          {
            title: "Sobremesa",
            description: "Doce de abóbora com coco",
            image: "https://via.placeholder.com/150/DAF7A6/000000?text=Doce",
          },
        ],
      },
    ],
  },
  {
    id: "cantina-italiana",
    name: "Cantina Italiana",
    address: "Avenida Principal, 456 - Bairro Antigo",
    cuisine: "Italiana",
    dailyMenus: [
      {
        dayOfWeek: "Segunda-feira",
        menuItems: [
          {
            title: "Entrada",
            description: "Bruschetta de tomate e manjericão",
            image:
              "https://via.placeholder.com/150/FF8C00/FFFFFF?text=Bruschetta",
          },
          {
            title: "Prato Principal",
            description: "Spaghetti à carbonara",
            notes: "(Contém bacon e ovo)",
            image:
              "https://via.placeholder.com/150/FF4500/FFFFFF?text=Carbonara",
          },
          {
            title: "Prato Vegano",
            description: "Pizza de legumes com massa integral",
            notes: "(Opção sem queijo)",
            image: "https://via.placeholder.com/150/FFD700/000000?text=Pizza",
          },
          {
            title: "Sobremesa",
            description: "Tiramisu",
            image:
              "https://via.placeholder.com/150/FFA07A/000000?text=Tiramisu",
          },
        ],
      },
      {
        dayOfWeek: "Terça-feira",
        menuItems: [
          {
            title: "Entrada",
            description: "Pão de alho com azeite",
            image:
              "https://via.placeholder.com/150/BDB76B/FFFFFF?text=PaoDeAlho",
          },
          {
            title: "Prato Principal",
            description: "Lasanha à bolonhesa",
            image: "https://via.placeholder.com/150/8B4513/FFFFFF?text=Lasanha",
          },
          {
            title: "Sobremesa",
            description: "Panna Cotta",
            image:
              "https://via.placeholder.com/150/D2B48C/000000?text=PannaCotta",
          },
        ],
      },
    ],
  },
];
