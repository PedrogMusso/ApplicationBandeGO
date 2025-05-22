import { View, type ViewProps, Text, Image } from "react-native"; // Importar Image

export type FoodCardProps = ViewProps & {
  lightColor?: string;
  darkColor?: string;
  image?: string; // URL ou source da imagem do prato
  title?: string; // Corresponde ao "Tipo de Prato/Categoria" (ex: "Entrada", "Prato Principal")
  description?: string; // Corresponde à "Descrição/Ingredientes" (ex: "Chicória, Pepino e molho de limão")
  notes?: string; // Nova propriedade para "Observações/Informações Adicionais" (ex: "(temos opção sem molho)")
};

export function FoodCard({
  style,
  lightColor, // Cores não usadas diretamente no componente, mas podem ser para um wrapper.
  darkColor, // Cores não usadas diretamente no componente, mas podem ser para um wrapper.
  image,
  title,
  description,
  notes, // Adicionado aqui
  ...otherProps
}: FoodCardProps) {
  return (
    <View
      className="flex flex-row min-h-[80px] w-full items-center justify-start bg-white rounded-lg shadow-md mb-4 overflow-hidden" // Adicionado shadow, rounded-lg, mb-4 e overflow-hidden para melhor visual
      style={style} // Aplicar o estilo passado via props
      {...otherProps}
    >
      <View className="flex w-[30%] justify-center items-center">
        {image ? (
          <Image
            source={{ uri: image }} // Usar URI para imagens da web ou {require(image)} para imagens locais
            className="w-full object-cover" // Ajustar a imagem para cobrir o espaço
          />
        ) : (
          <Text className="text-gray-500 text-xs">Sem imagem</Text> // Placeholder mais informativo
        )}
      </View>
      <View className="flex flex-col flex-grow p-3 justify-center">
        {/* flex-grow para ocupar o espaço restante, p-3 para padding */}
        {title && (
          <Text className="text-lg font-bold text-gray-800 mb-1">{title}</Text>
        )}
        {description && (
          <Text className="text-sm text-gray-600">{description}</Text>
        )}
        {notes && ( // Renderizar as notas apenas se existirem
          <Text className="text-xs text-gray-500 mt-1 italic">{notes}</Text>
        )}
      </View>
    </View>
  );
}
