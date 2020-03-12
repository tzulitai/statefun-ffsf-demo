package org.ffsf.demo.inventory;

import com.google.protobuf.Any;
import org.apache.flink.statefun.sdk.Context;
import org.apache.flink.statefun.sdk.FunctionType;
import org.apache.flink.statefun.sdk.annotations.Persisted;
import org.apache.flink.statefun.sdk.match.MatchBinder;
import org.apache.flink.statefun.sdk.match.StatefulMatchFunction;
import org.apache.flink.statefun.sdk.state.PersistedValue;
import org.ffsf.demo.inventory.generated.ProtobufMessages.RestockItem;
import org.ffsf.demo.inventory.generated.ProtobufMessages.RequestItem;
import org.ffsf.demo.inventory.generated.ProtobufMessages.ItemAvailability;

public final class FnInventory extends StatefulMatchFunction {

    static final FunctionType TYPE = new FunctionType("org.ffsf.demo", "inventory");

    @Persisted
    private final PersistedValue<Integer> quantity = PersistedValue.of("quantity", Integer.class);

    @Override
    public void configure(MatchBinder matchBinder) {
        matchBinder
                .predicate(Any.class, any -> any.is(RequestItem.class), this::handleItemRequest)
                .predicate(RestockItem.class, this::handleItemRestock);
    }

    private void handleItemRestock(Context context, RestockItem restock) {
        try {
            int currentQuantity = quantity.getOrDefault(0) + restock.getQuantity();
            quantity.set(currentQuantity);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    private void handleItemRequest(Context context, Any message) {
        try {
            RequestItem request = message.unpack(RequestItem.class);

            int currentQuantity = quantity.getOrDefault(0);
            int requestedAmount = request.getQuantity();

            ItemAvailability.Builder availability =
                    ItemAvailability.newBuilder().setQuantity(requestedAmount);

            if (currentQuantity >= requestedAmount) {
                quantity.set(currentQuantity - requestedAmount);
                availability.setStatus(ItemAvailability.Status.IN_STOCK);
            } else {
                availability.setStatus(ItemAvailability.Status.OUT_OF_STOCK);
            }
            context.reply(Any.pack(availability.build()));
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}
