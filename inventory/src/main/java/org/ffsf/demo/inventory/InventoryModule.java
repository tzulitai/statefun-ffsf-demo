package org.ffsf.demo.inventory;

import com.google.auto.service.AutoService;
import org.apache.flink.statefun.sdk.io.IngressIdentifier;
import org.apache.flink.statefun.sdk.io.IngressSpec;
import org.apache.flink.statefun.sdk.kafka.KafkaIngressBuilder;
import org.apache.flink.statefun.sdk.kafka.KafkaIngressDeserializer;
import org.apache.flink.statefun.sdk.kafka.KafkaIngressStartupPosition;
import org.apache.flink.statefun.sdk.spi.StatefulFunctionModule;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.ffsf.demo.inventory.generated.ProtobufMessages.RestockItem;

import java.util.Map;

@AutoService(StatefulFunctionModule.class)
public class InventoryModule implements StatefulFunctionModule {
    @Override
    public void configure(Map<String, String> map, Binder binder) {
        binder.bindFunctionProvider(FnInventory.TYPE, ignored -> new FnInventory());
        binder.bindIngress(restockItemIngressSpec());
        binder.bindIngressRouter(
                new IngressIdentifier<>(RestockItem.class, "org.ffsf.demo", "inventory-restock-events"),
                ((restockItem, downstream) -> downstream.forward(FnInventory.TYPE, restockItem.getItemId(), restockItem))
        );
    }

    private static IngressSpec<RestockItem> restockItemIngressSpec() {
        return KafkaIngressBuilder.forIdentifier(new IngressIdentifier<>(RestockItem.class, "org.ffsf.demo", "inventory-restock-events"))
                .withConsumerGroupId("demo")
                .withKafkaAddress("kafka-broker:29092")
                .withStartupPosition(KafkaIngressStartupPosition.fromEarliest())
                .withTopic("inventory-restock-events")
                .withDeserializer(RestockItemEventDeserializer.class)
                .build();
    }

    public static final class RestockItemEventDeserializer implements KafkaIngressDeserializer<RestockItem> {
        @Override
        public RestockItem deserialize(ConsumerRecord<byte[], byte[]> consumerRecord) {
            try {
                return RestockItem.parseFrom(consumerRecord.value());
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        }
    }
}
