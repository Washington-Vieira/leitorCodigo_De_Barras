from app.utils.db_checker import verificar_duplicatas, limpar_duplicatas, adicionar_restricoes

def main():
    print("Verificando duplicatas no banco de dados...")
    duplicatas = verificar_duplicatas()
    
    if not duplicatas['produtos'] and not duplicatas['leituras']:
        print("✅ Não foram encontradas duplicatas no banco de dados!")
        return
    
    print("\n🔍 Duplicatas encontradas:")
    
    if duplicatas['produtos']:
        print("\nDuplicatas na tabela produtos:")
        for dup in duplicatas['produtos']:
            print(f"Serial: {dup[0]}, Máquina: {dup[1]}, Quantidade: {dup[2]}")
    
    if duplicatas['leituras']:
        print("\nDuplicatas na tabela leituras:")
        for dup in duplicatas['leituras']:
            print(f"Serial: {dup[0]}, Pedido: {dup[1]}, Linha: {dup[2]}, Data: {dup[3]}, Hora: {dup[4]}, Quantidade: {dup[5]}")
    
    resposta = input("\nDeseja remover as duplicatas? (s/n): ")
    if resposta.lower() == 's':
        print("\nRemovendo duplicatas...")
        limpar_duplicatas()
        print("✅ Duplicatas removidas com sucesso!")
        
        print("\nAdicionando restrições para prevenir futuras duplicatas...")
        adicionar_restricoes()
        print("✅ Restrições adicionadas com sucesso!")

if __name__ == "__main__":
    main() 